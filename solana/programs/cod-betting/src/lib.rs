use anchor_lang::prelude::*;
use anchor_spl::token::{self, Token, TokenAccount, Mint, Transfer};
use anchor_spl::associated_token::AssociatedToken;

declare_id!("Fg6PaFpoGXkYsidMpWTK6W2BeZ7FEfcYkg476zPFsLnS");

#[program]
pub mod cod_betting {
    use super::*;

    pub fn initialize_bet(
        ctx: Context<InitializeBet>,
        amount: u64,
        bet_seed: String,
    ) -> Result<()> {
        let bet = &mut ctx.accounts.bet;
        bet.creator = ctx.accounts.creator.key();
        bet.amount = amount;
        bet.state = BetState::Created;
        bet.seed = bet_seed;
        
        // Transfer tokens to escrow
        let transfer_ctx = CpiContext::new(
            ctx.accounts.token_program.to_account_info(),
            Transfer {
                from: ctx.accounts.creator_token.to_account_info(),
                to: ctx.accounts.escrow_token.to_account_info(),
                authority: ctx.accounts.creator.to_account_info(),
            },
        );
        token::transfer(transfer_ctx, amount)?;
        
        Ok(())
    }

    pub fn join_bet(
        ctx: Context<JoinBet>,
        amount: u64,
    ) -> Result<()> {
        let bet = &mut ctx.accounts.bet;
        require!(bet.state == BetState::Created, BetError::InvalidBetState);
        require!(amount == bet.amount, BetError::AmountMismatch);

        // Transfer matching tokens to escrow
        let transfer_ctx = CpiContext::new(
            ctx.accounts.token_program.to_account_info(),
            Transfer {
                from: ctx.accounts.joiner_token.to_account_info(),
                to: ctx.accounts.escrow_token.to_account_info(),
                authority: ctx.accounts.joiner.to_account_info(),
            },
        );
        token::transfer(transfer_ctx, amount)?;

        bet.joiner = Some(ctx.accounts.joiner.key());
        bet.state = BetState::Active;
        
        Ok(())
    }

    pub fn settle_bet(
        ctx: Context<SettleBet>,
        winner: Pubkey,
    ) -> Result<()> {
        let bet = &mut ctx.accounts.bet;
        require!(bet.state == BetState::Active, BetError::InvalidBetState);
        
        // Verify winner is either creator or joiner
        require!(
            winner == bet.creator || winner == bet.joiner.unwrap(),
            BetError::InvalidWinner
        );

        // Transfer all tokens to winner
        let total_amount = bet.amount * 2;
        let transfer_ctx = CpiContext::new_with_signer(
            ctx.accounts.token_program.to_account_info(),
            Transfer {
                from: ctx.accounts.escrow_token.to_account_info(),
                to: ctx.accounts.winner_token.to_account_info(),
                authority: ctx.accounts.escrow_token.to_account_info(),
            },
            &[&[
                b"escrow",
                bet.seed.as_bytes(),
                &[ctx.bumps.escrow_token],
            ]],
        );
        token::transfer(transfer_ctx, total_amount)?;

        bet.state = BetState::Completed;
        bet.winner = Some(winner);
        
        Ok(())
    }
}

#[derive(Accounts)]
#[instruction(amount: u64, bet_seed: String)]
pub struct InitializeBet<'info> {
    #[account(mut)]
    pub creator: Signer<'info>,
    
    #[account(
        init,
        payer = creator,
        space = Bet::space(),
        seeds = [b"bet", bet_seed.as_bytes()],
        bump
    )]
    pub bet: Account<'info, Bet>,
    
    #[account(
        mut,
        associated_token::mint = mint,
        associated_token::authority = creator,
    )]
    pub creator_token: Account<'info, TokenAccount>,
    
    #[account(
        init,
        payer = creator,
        seeds = [b"escrow", bet_seed.as_bytes()],
        bump,
        token::mint = mint,
        token::authority = escrow_token,
    )]
    pub escrow_token: Account<'info, TokenAccount>,
    
    pub mint: Account<'info, Mint>,
    pub system_program: Program<'info, System>,
    pub token_program: Program<'info, Token>,
    pub associated_token_program: Program<'info, AssociatedToken>,
    pub rent: Sysvar<'info, Rent>,
}

#[derive(Accounts)]
pub struct JoinBet<'info> {
    #[account(mut)]
    pub joiner: Signer<'info>,
    
    #[account(mut)]
    pub bet: Account<'info, Bet>,
    
    #[account(
        mut,
        associated_token::mint = mint,
        associated_token::authority = joiner,
    )]
    pub joiner_token: Account<'info, TokenAccount>,
    
    #[account(mut)]
    pub escrow_token: Account<'info, TokenAccount>,
    
    pub mint: Account<'info, Mint>,
    pub token_program: Program<'info, Token>,
}

#[derive(Accounts)]
pub struct SettleBet<'info> {
    #[account(mut)]
    pub bet: Account<'info, Bet>,
    
    #[account(mut)]
    pub escrow_token: Account<'info, TokenAccount>,
    
    #[account(mut)]
    pub winner_token: Account<'info, TokenAccount>,
    
    pub token_program: Program<'info, Token>,
}

#[account]
pub struct Bet {
    pub creator: Pubkey,
    pub joiner: Option<Pubkey>,
    pub winner: Option<Pubkey>,
    pub amount: u64,
    pub state: BetState,
    pub seed: String,
}

impl Bet {
    pub fn space() -> usize {
        8 +  // discriminator
        32 + // creator
        33 + // joiner (Option)
        33 + // winner (Option)
        8 +  // amount
        1 +  // state
        36   // seed (String)
    }
}

#[derive(AnchorSerialize, AnchorDeserialize, Clone, PartialEq)]
pub enum BetState {
    Created,
    Active,
    Completed,
}

#[error_code]
pub enum BetError {
    #[msg("Invalid bet state for this operation")]
    InvalidBetState,
    #[msg("Bet amount must match creator's amount")]
    AmountMismatch,
    #[msg("Winner must be either creator or joiner")]
    InvalidWinner,
} 