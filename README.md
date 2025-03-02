# COD P2P Betting Platform

A peer-to-peer betting platform for Call of Duty matches, built with FastAPI, React Native, and Solana. Uses ChatGPT Vision API for automated match result verification.

## Features

- Create and join P2P bets on COD match outcomes
- Upload post-game screenshots for automated verification
- ChatGPT Vision API for accurate stat extraction from screenshots
- Solana-based token system for secure betting and payouts
- React Native iOS app for mobile-first experience

## Tech Stack

- **Backend**: Python FastAPI
- **Frontend**: React Native (iOS)
- **Blockchain**: Solana (SPL Tokens & Smart Contracts)
- **Image Processing**: OpenAI GPT-4 Vision API
- **Database**: PostgreSQL (not implemented in prototype)

## Getting Started

### Prerequisites

- Python 3.8+
- Node.js 16+
- Solana CLI tools
- iOS development environment (Xcode)
- OpenAI API key with GPT-4 Vision access

### Backend Setup

1. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up environment variables:
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   # Make sure to add your OpenAI API key
   ```

4. Run the FastAPI server:
   ```bash
   uvicorn app.main:app --reload
   ```

### Frontend Setup

The React Native frontend is not included in this prototype. It would include:

- Camera integration for screenshot capture
- Solana wallet integration
- Bet creation and management UI
- Real-time updates for bet status

### Solana Setup

1. Install Solana CLI tools
2. Create a development wallet
3. Switch to devnet
4. Deploy the betting program (smart contract)

## API Endpoints

### Bets

- `POST /bets/create` - Create a new bet
- `POST /bets/join/{bet_id}` - Join an existing bet
- `POST /bets/verify` - Submit match results for verification (uses ChatGPT Vision)
- `GET /bets/active` - List active bets

### Authentication (To Be Implemented)

- `POST /auth/register` - Register new user
- `POST /auth/login` - Login user

## Architecture

```
┌─────────────────────────────┐
│         iOS App (RN)        │
│(Takes Photo, Places Bets,   │
│Submits to Backend)          │
└───────▲─────────────────────┘
        │
        │   REST/WebSocket
        │
┌───────┴─────────────────────┐
│       FastAPI Backend       │
│  (Auth, Bets, Image Parsing,│
│   Solana Integration)       │
└───────▲─────────────────────┘
        │
        │   GPT-4 Vision API
        │
┌───────┴─────────────────────┐
│     OpenAI ChatGPT API      │
│  (Screenshot Analysis)      │
└───────▲─────────────────────┘
        │
        │   On successful parse
        │
┌───────┴─────────────────────┐
│        Solana Network       │
│ (Smart Contract, Escrow,    │
│  Payout in SPL Token)       │
└─────────────────────────────┘
```

## Development Status

This is a prototype implementation demonstrating the core architecture and flow. To make it production-ready, you would need to:

1. Implement proper database models and migrations
2. Add comprehensive authentication and authorization
3. Develop the React Native frontend
4. Create and deploy Solana smart contracts
5. Fine-tune ChatGPT prompts for better accuracy
6. Add proper error handling and logging
7. Implement WebSocket for real-time updates
8. Add comprehensive testing
9. Implement rate limiting for API usage

## Security Considerations

- Implement proper wallet security measures
- Add rate limiting for API endpoints
- Validate and sanitize all user inputs
- Secure storage of API keys and secrets
- Implement proper session management
- Add fraud detection for screenshot submissions
- Monitor and optimize OpenAI API usage

## Cost Considerations

The platform uses the GPT-4 Vision API, which has associated costs:

- GPT-4 Vision API: $0.01 per image
- Consider implementing caching for repeated submissions
- Monitor API usage and implement rate limiting
- Consider batch processing for cost optimization

## License

[MIT License](LICENSE)

## Contributing

This is a prototype project. For a production version, please fork and submit pull requests. 