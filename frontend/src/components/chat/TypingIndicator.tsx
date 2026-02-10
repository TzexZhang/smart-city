import React from 'react'
import { motion } from 'framer-motion'

interface TypingIndicatorProps {
  visible?: boolean
}

const TypingIndicator: React.FC<TypingIndicatorProps> = ({ visible = true }) => {
  if (!visible) return null

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -10 }}
      style={styles.container}
    >
      <div style={styles.bubble}>
        <div style={styles.dotsContainer}>
          {[0, 1, 2].map((i) => (
            <motion.div
              key={i}
              style={styles.dot}
              animate={{
                scale: [1, 1.2, 1],
                opacity: [0.5, 1, 0.5],
              }}
              transition={{
                duration: 1.2,
                repeat: Infinity,
                delay: i * 0.2,
              }}
            />
          ))}
        </div>
      </div>
    </motion.div>
  )
}

const styles: Record<string, React.CSSProperties> = {
  container: {
    marginBottom: 16,
    marginLeft: 0,
  },
  bubble: {
    display: 'inline-block',
    background: 'rgba(255, 255, 255, 0.95)',
    backdropFilter: 'blur(20px)',
    border: '1px solid rgba(255, 255, 255, 0.3)',
    borderRadius: 16,
    borderBottomLeftRadius: 4,
    padding: '12px 16px',
    boxShadow: '0 2px 8px rgba(0, 0, 0, 0.1)',
  },
  dotsContainer: {
    display: 'flex',
    gap: 6,
    alignItems: 'center',
  },
  dot: {
    width: 8,
    height: 8,
    borderRadius: '50%',
    background: '#1890ff',
  },
}

export default TypingIndicator
