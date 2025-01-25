# S.P.A.R.C - Smart Personalised Automation for Remarkable Campaigns

SPARC is an AI-powered marketing campaign generator that helps create, manage, and distribute personalized campaign content across multiple platforms.

## 🌟 Features

- **AI-Powered Content Generation**: Leverages Azure OpenAI to create engaging content
- **Persona Management**: Create and manage detailed target audience personas
- **Multi-Platform Distribution**:
  - Twitter integration for social media posting
  - Email campaign management
- **Campaign Analytics**: Track performance metrics across platforms
  - Impressions
  - Click-through rates
  - Conversions
  - ROI tracking
- **Content History**: Maintain a record of all generated content with reusability options

## 🚀 Getting Started

### Prerequisites

- Python 3.8+
- Azure OpenAI API access
- Twitter Developer Account (for Twitter integration)
- SMTP server access (for email campaigns)

### Installation

1. Clone the repository:

```bash
git clone https://github.com/yourusername/sparc.git
cd sparc
```

2. Create and activate a virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # For Unix/macOS
venv\Scripts\activate     # For Windows
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Create a `.env` file in the root directory with your credentials:

```env
AZURE_OPENAI_API_KEY=your_azure_openai_api_key
AZURE_OPENAI_ENDPOINT=your_azure_endpoint
TWITTER_API_KEY=your_twitter_api_key
TWITTER_API_SECRET=your_twitter_api_secret
TWITTER_ACCESS_TOKEN=your_twitter_access_token
TWITTER_ACCESS_TOKEN_SECRET=your_twitter_access_token_secret
EMAIL_SMTP_USER=your_email
EMAIL_SMTP_PASSWORD=your_email_password
```

### Running the Application

```bash
streamlit run app.py
```

## 📋 Usage

1. **Create Personas**
   - Navigate to "Create Persona"
   - Fill in persona details
   - Save persona for future use

2. **Generate Content**
   - Select target personas
   - Define campaign goals
   - Choose content type and tone
   - Add relevant hashtags
   - Generate AI-powered content

3. **Distribute Content**
   - Preview and post to Twitter
   - Send email campaigns
   - Track performance in analytics

4. **Analytics**
   - View performance metrics
   - Track engagement across platforms
   - Monitor ROI and conversions

## 🔧 Configuration

The application uses a `config.yaml` file for various settings:

```yaml
azure_openai:
  deployment_name: gpt-4
  api_version: 2024-02-15-preview

email:
  smtp_server: smtp.gmail.com
  smtp_port: 587
```

## 📊 Analytics Features

- Real-time performance tracking
- Platform-specific metrics
- Time-period filtering
- Visual trend analysis
- Detailed campaign reporting

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Azure OpenAI for AI capabilities
- Streamlit for the web interface
- Twitter API for social media integration

## 📞 Support

For support, email support@sparc.ai or open an issue in the repository.

## 🔮 Future Enhancements

- LinkedIn integration
- Advanced analytics with ML-powered insights
- Custom template management
- Automated scheduling
- A/B testing capabilities
