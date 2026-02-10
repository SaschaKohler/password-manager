# Password Manager Suite

A secure, open-source password manager built with Django, Python, and Kubernetes. Inspired by Dashlane, this project provides enterprise-grade password management with end-to-end encryption.

## 🚀 Vibe-Coding Project

This is a **vibe-coding** project - an experimental side project and proof of concept exploring AI-assisted development workflows. Built with passion and curiosity, demonstrating what's possible when human creativity meets AI collaboration.

### 🤖 AI Development Stack
- **Primary Tools**: Windsurf & KiloSoft for AI-assisted coding
- **Editor**: Neovim 0.12 with default vim.pack configuration
- **Infrastructure**: w4y server deployment
- **Code Review**: Human brain + AI assistance for quality assurance

### 🎯 Project Philosophy
> "Code with vibes, ship with confidence"

This project embraces the modern AI-assisted development paradigm where:
- **Speed meets quality** through AI-human collaboration
- **Learning happens** through iterative development
- **Innovation thrives** in experimental playgrounds

## 🚀 Features

- **Secure Password Storage**: AES-256 encryption with user-controlled master keys
- **Two-Factor Authentication**: TOTP and backup codes support
- **Password Generator**: Customizable secure password generation
- **Team Management**: Secure password sharing for teams
- **Dark Web Monitoring**: Automated breach detection
- **Cross-Platform**: Web, desktop, and mobile applications
- **Kubernetes Ready**: Cloud-native deployment with auto-scaling
- **AI-Assisted Development**: Built with modern AI coding tools

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Django API    │    │   PostgreSQL    │
│   (React/Vue)   │◄──►│   (REST/GraphQL)│◄──►│   (Encrypted)   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌─────────────────┐
                       │   Redis Cache   │
                       │   (Sessions)    │
                       └─────────────────┘
```

### 🤖 AI Development Architecture
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Windsurf AI   │    │   KiloSoft AI   │    │   Human Brain   │
│   (Code Gen)    │◄──►│   (Review)      │◄──►│   (Decisions)   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌─────────────────┐
                       │   Neovim 0.12   │
                       │   (vim.pack)    │
                       └─────────────────┘
```

## 🛠️ Tech Stack

### Backend & Core
- **Backend**: Django 5.0+, Django REST Framework
- **Database**: PostgreSQL 15+
- **Cache**: Redis 7+
- **Security**: Cryptography, TOTP, JWT

### AI Development Environment
- **AI Assistants**: Windsurf, KiloSoft (primary coding partners)
- **Editor**: Neovim 0.12 + vim.pack (minimal, efficient setup)
- **Deployment**: w4y server infrastructure
- **Review Process**: Human brain validation + AI suggestions

### Frontend & Infrastructure
- **Frontend**: React 18+ / Vue 3+ (when we get there)
- **Containerization**: Docker, Docker Compose
- **Orchestration**: Kubernetes, Helm
- **Testing**: pytest, Playwright
- **Package Management**: uv
- **CI/CD**: GitHub Actions

## 📦 Quick Start

### Prerequisites

- Python 3.11+
- Docker & Docker Compose
- Kubernetes cluster (for production)
- uv (Python package manager)

### Local Development

```bash
# Clone the repository
git clone https://github.com/your-username/password-manager.git
cd password-manager

# Setup Python environment with uv
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
uv pip install -e .

# Setup database
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Run development server
python manage.py runserver
```

### Docker Development

```bash
# Build and run with Docker Compose
docker-compose up --build
```

### Kubernetes Deployment

```bash
# Deploy to Kubernetes
kubectl apply -f k8s/
```

## 🔐 Security Features

- **End-to-End Encryption**: Client-side encryption before storage
- **Zero-Knowledge Architecture**: Server never sees plaintext passwords
- **Secure Key Derivation**: PBKDF2 with random salts
- **Session Management**: Secure JWT tokens with refresh rotation
- **Rate Limiting**: Protection against brute force attacks
- **Audit Logging**: Complete access tracking

## 📚 Documentation

- [Development Guide](./AGENTS.md) - Development setup and best practices
- [API Documentation](./docs/api.md) - REST API reference
- [Security Architecture](./docs/security.md) - Security implementation details
- [Deployment Guide](./docs/deployment.md) - Production deployment instructions

## 🧪 Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=.

# Run security tests
bandit -r ./
```

## 🤝 Contributing

This is a vibe-coding project - contributions are welcome but keep the vibes! Please read [AGENTS.md](./AGENTS.md) for detailed development guidelines and best practices.

### AI Development Guidelines
- **Human-first**: AI assists, human decides
- **Quality matters**: Even vibe-coding needs standards
- **Learn openly**: Share discoveries and techniques
- **Iterate fast**: Build, measure, learn, repeat

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## ⚠️ Security Notice

This is a **proof of concept** and vibe-coding project. For production use, ensure:
- Proper security audit by human experts
- Hardening of infrastructure
- Regular security updates
- Compliance with relevant regulations

## 🧠 AI-Human Collaboration Notes

This project demonstrates the power of AI-assisted development while maintaining human oversight:
- **AI handles**: Boilerplate, patterns, documentation
- **Human validates**: Security decisions, architecture, user experience
- **Together we**: Build faster, learn continuously, ship quality

## 🙏 Acknowledgments

- Inspired by Dashlane's password management approach
- Built with Django's security-first philosophy
- Kubernetes-native design for scalability
- **Special thanks**: All AI assistants helping make this possible
- **Human credit**: The brain behind the decisions and reviews
