# Contributing to YouTube to Blog Converter

Thank you for your interest in contributing to this Bolt.new hackathon project! We welcome contributions from developers of all skill levels.

## 🚀 Getting Started

1. **Fork the repository**
2. **Clone your fork locally**
   ```bash
   git clone https://github.com/yourusername/youtube-to-blog-converter.git
   cd youtube-to-blog-converter
   ```
3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```
4. **Create a new branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

## 🎯 Areas for Contribution

### 🐛 Bug Fixes
- Report bugs through GitHub Issues
- Include steps to reproduce
- Provide system information (OS, Python version, browser)

### ✨ New Features
- **New Blog Templates**: Add creative template formats
- **UI/UX Improvements**: Enhance user experience
- **Performance Optimizations**: Improve loading times
- **Mobile Enhancements**: Better mobile responsiveness

### 🔧 Technical Improvements
- **Error Handling**: More robust error recovery
- **API Integrations**: Support for additional video platforms
- **Caching**: Improved caching mechanisms
- **Testing**: Add unit and integration tests

### 📚 Documentation
- Improve README sections
- Add code comments
- Create tutorial videos
- Update API documentation

## 📋 Contribution Guidelines

### Code Style
- Follow Python PEP 8 for backend code
- Use meaningful variable and function names
- Add comments for complex logic
- Keep functions focused and small

### Frontend Guidelines
- Use modern JavaScript (ES6+)
- Follow consistent naming conventions
- Ensure responsive design
- Test across different browsers

### Git Workflow
1. **Create descriptive commit messages**
   ```bash
   git commit -m "Add: Progressive loading for blog generation"
   git commit -m "Fix: Template caching issue with special characters"
   git commit -m "Update: README with deployment instructions"
   ```

2. **Keep commits focused**
   - One feature/fix per commit
   - Avoid mixing unrelated changes

3. **Update documentation**
   - Update README if adding features
   - Add inline code comments
   - Update API documentation

### Pull Request Process
1. **Ensure your code works**
   - Test thoroughly before submitting
   - Check both frontend and backend functionality

2. **Create a clear PR description**
   ```markdown
   ## What does this PR do?
   - Adds progressive loading animation
   - Improves user experience during video processing

   ## How to test?
   1. Enter a YouTube URL
   2. Click convert and observe the new loading states
   3. Verify all steps complete successfully

   ## Screenshots (if applicable)
   [Add screenshots of UI changes]
   ```

3. **Link related issues**
   - Reference issue numbers: "Fixes #123"
   - Explain how your changes address the issue

## 🧪 Testing Your Changes

### Backend Testing
```bash
# Start the server
python run_server.py

# Test API endpoints
curl http://localhost:8000/api/health
```

### Frontend Testing
1. Open `http://localhost:8000` in browser
2. Test with various YouTube URLs:
   - Standard videos: `https://youtube.com/watch?v=dQw4w9WgXcQ`
   - Short URLs: `https://youtu.be/dQw4w9WgXcQ`
   - Long videos (test loading states)
   - Videos without transcripts (test fallbacks)

### Cross-browser Testing
- Chrome (recommended)
- Firefox
- Edge
- Safari (if available)

## 🎨 Design Guidelines

### Color Scheme
- Primary: Blue (#3B82F6)
- Success: Green (#10B981)
- Warning: Yellow (#F59E0B)
- Error: Red (#EF4444)
- Gray scale for text and backgrounds

### Typography
- Headlines: Bold, clear hierarchy
- Body text: Readable, good contrast
- Code: Monospace font

### Animations
- Smooth transitions (300ms)
- Progressive loading states
- Hover effects for interactivity

## 🚨 Issue Reporting

### Bug Reports
Include:
- **Description**: What happened?
- **Steps to reproduce**: How can we reproduce it?
- **Expected behavior**: What should have happened?
- **System info**: OS, browser, Python version
- **Screenshots**: If applicable

### Feature Requests
Include:
- **Problem**: What problem would this solve?
- **Solution**: Describe your proposed solution
- **Alternatives**: Any alternative solutions considered?
- **Use case**: How would this benefit users?

## 📞 Getting Help

- **GitHub Issues**: For bugs and feature requests
- **Discussions**: For questions and general discussion
- **Documentation**: Check the README first

## 🏆 Recognition

Contributors will be:
- Listed in the README contributors section
- Mentioned in release notes for significant contributions
- Credited in the project's acknowledgments

Thank you for helping make this project better! 🚀 