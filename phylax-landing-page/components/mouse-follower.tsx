'use client';

import React, { useEffect, useState } from 'react';
import { motion, useMotionValue, useSpring } from 'framer-motion';

export function MouseFollower() {
  const [isHovering, setIsHovering] = useState(false);
  const [isVisible, setIsVisible] = useState(false);

  // useMotionValue for raw mouse position (0 latency)
  const cursorX = useMotionValue(-100);
  const cursorY = useMotionValue(-100);

  // useSpring for smooth and snappy interpolation without bouncing
  const springConfig = { damping: 30, stiffness: 400, mass: 0.1 };
  const cursorXSpring = useSpring(cursorX, springConfig);
  const cursorYSpring = useSpring(cursorY, springConfig);

  useEffect(() => {
    setIsVisible(true);

    const updateMousePosition = (e: MouseEvent) => {
      cursorX.set(e.clientX - 12);
      cursorY.set(e.clientY - 12);
    };

    const handleMouseOver = (e: MouseEvent) => {
      const target = e.target as HTMLElement;
      if (
        target.closest('button') || 
        target.closest('a') || 
        target.tagName.toLowerCase() === 'input'
      ) {
        setIsHovering(true);
      } else {
        setIsHovering(false);
      }
    };

    window.addEventListener('mousemove', updateMousePosition);
    window.addEventListener('mouseover', handleMouseOver);

    return () => {
      window.removeEventListener('mousemove', updateMousePosition);
      window.removeEventListener('mouseover', handleMouseOver);
    };
  }, [cursorX, cursorY]);

  if (!isVisible) return null;

  return (
    <motion.div
      className="pointer-events-none fixed top-0 left-0 z-[100] hidden md:block" // Hidden on mobile
      style={{
        x: cursorXSpring,
        y: cursorYSpring,
      }}
    >
      <div 
        className={`transition-all duration-300 ease-out flex items-center justify-center ${
          isHovering 
            ? 'w-20 h-20 -ml-4 -mt-4 rounded-2xl bg-gradient-to-br from-white/40 to-white/10 backdrop-blur-md border border-white/50 shadow-[0_8px_32px_rgba(0,0,0,0.1)]' 
            : 'w-6 h-6 rounded-full bg-coffee-bean/10 border border-coffee-bean/20 mix-blend-multiply'
        }`} 
      />
    </motion.div>
  );
}
