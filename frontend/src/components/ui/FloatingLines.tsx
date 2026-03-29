import React, { useEffect, useRef } from "react";

interface FloatingLinesProps {
  strokeColor?: string;
  strokeWidth?: number;
  lineCount?: number;
  speed?: number;
  className?: string;
}

export default function FloatingLines({
  strokeColor = "rgba(99, 102, 241, 0.2)",
  strokeWidth = 1,
  lineCount = 15,
  speed = 0.5,
  className = "",
}: FloatingLinesProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    let animationFrameId: number;
    let width = window.innerWidth;
    let height = window.innerHeight;

    const resize = () => {
      width = window.innerWidth;
      height = window.innerHeight;
      canvas.width = width;
      canvas.height = height;
    };

    window.addEventListener("resize", resize);
    resize();

    interface Line {
      x: number;
      y: number;
      length: number;
      speed: number;
      opacity: number;
    }

    const lines: Line[] = [];
    for (let i = 0; i < lineCount; i++) {
      lines.push({
        x: Math.random() * width,
        y: Math.random() * height,
        length: Math.random() * 200 + 100,
        speed: (Math.random() * 0.5 + 0.1) * speed,
        opacity: Math.random() * 0.5 + 0.1,
      });
    }

    const draw = () => {
      ctx.clearRect(0, 0, width, height);
      ctx.strokeStyle = strokeColor;
      ctx.lineWidth = strokeWidth;

      lines.forEach((line) => {
        ctx.beginPath();
        ctx.moveTo(line.x, line.y);
        ctx.lineTo(line.x + line.length, line.y - line.length / 2);
        ctx.stroke();

        line.x += line.speed;
        line.y -= line.speed / 2;

        if (line.x > width || line.y < 0) {
          line.x = -line.length;
          line.y = Math.random() * height + line.length;
        }
      });

      animationFrameId = requestAnimationFrame(draw);
    };

    draw();

    return () => {
      window.removeEventListener("resize", resize);
      cancelAnimationFrame(animationFrameId);
    };
  }, [strokeColor, strokeWidth, lineCount, speed]);

  return (
    <canvas
      ref={canvasRef}
      className={`absolute inset-0 pointer-events-none ${className}`}
      style={{ mixBlendMode: "normal" }}
    />
  );
}
