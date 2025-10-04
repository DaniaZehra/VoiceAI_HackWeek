# Voice Command POS Frontend

A modern, responsive Point of Sale (POS) web application with voice command functionality built using Next.js, React, and Tailwind CSS.

## Features

- **Voice Recording**: Record audio directly in the browser
- **File Upload**: Upload WAV/audio files for transcription
- **Dashboard**: Real-time sales summary and statistics
- **Modern UI**: Clean, professional design with soft colors and shadows
- **Responsive**: Works on desktop, tablet, and mobile devices
- **Urdu Support**: Full RTL support for Urdu text
- **Fast API Integration**: Connects to FastAPI backend for STT processing

## Voice Commands

The system recognizes the following Urdu voice commands:
- **"سیلز"** - Shows sales report
- **"پروڈکٹ"** - Shows product list
- **"بل"** - Opens billing screen

## Tech Stack

- **Frontend**: Next.js 15, React 18, TypeScript
- **Styling**: Tailwind CSS
- **Icons**: Emoji icons for modern look
- **Audio**: Web Audio API for recording
- **Backend Integration**: FastAPI (Python)

## Getting Started

### Prerequisites

- Node.js 18+ 
- npm or yarn
- FastAPI backend running on `http://localhost:8000`

### Installation

1. **Clone and navigate to the project:**
   ```bash
   cd voice-pos-app
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Start the development server:**
   ```bash
   npm run dev
   ```

4. **Open your browser:**
   Navigate to `http://localhost:3000`

### Backend Setup

Make sure your FastAPI backend is running on `http://localhost:8000` with the `/voice-command` endpoint available.

## Project Structure

```
voice-pos-app/
├── src/
│   ├── app/
│   │   ├── globals.css      # Global styles and Tailwind config
│   │   ├── layout.tsx       # Root layout with metadata
│   │   └── page.tsx        # Main page component
│   └── components/
│       ├── Dashboard.tsx    # Sales dashboard with cards
│       └── VoiceCommand.tsx # Voice recording and upload
├── tailwind.config.ts       # Tailwind configuration
└── package.json
```

## Usage

1. **Voice Recording:**
   - Click the microphone button to start recording
   - Click again to stop and process the audio
   - The system will transcribe and respond to your command

2. **File Upload:**
   - Click the file upload area to select an audio file
   - Supported formats: WAV, MP3, and other audio formats
   - The file will be processed automatically

3. **Dashboard:**
   - View real-time sales data
   - Click on action cards for different functions
   - All interactions are voice-controlled

## API Integration

The frontend communicates with the FastAPI backend:

```typescript
// POST /voice-command
const formData = new FormData();
formData.append('file', audioBlob, 'recording.wav');

const response = await fetch('http://localhost:8000/voice-command', {
  method: 'POST',
  body: formData,
});
```

## Customization

### Colors and Styling
- Modify `tailwind.config.ts` for custom colors
- Update `globals.css` for additional styles
- All components use Tailwind utility classes

### Voice Commands
- Update the backend STT processing logic
- Modify the instruction text in `VoiceCommand.tsx`

### Dashboard Data
- Replace dummy data in `Dashboard.tsx` with real API calls
- Add more action cards as needed

## Browser Support

- Chrome/Edge: Full support including audio recording
- Firefox: Full support including audio recording  
- Safari: Full support including audio recording
- Mobile browsers: Responsive design works on all devices

## Development

### Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run start` - Start production server
- `npm run lint` - Run ESLint

### Environment Variables

Create a `.env.local` file for environment-specific settings:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is licensed under the MIT License.

## Support

For issues and questions:
- Check the browser console for errors
- Ensure the backend API is running
- Verify microphone permissions are granted
- Check network connectivity