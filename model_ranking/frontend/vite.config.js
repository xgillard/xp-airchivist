import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  optimizeDeps: {
    include: [
      '@mui/material',
      '@emotion/styled',
      '@mui/icons-material',
      "@mui/icons-material/Stars",
      "@mui/icons-material/ArrowBackIos",
      "@mui/icons-material/ArrowForwardIos",
      "@mui/icons-material/EmojiPeople",
      "@mui/icons-material/CalendarMonth",
      "@mui/icons-material/ExpandMore",
    ],
  },
})
