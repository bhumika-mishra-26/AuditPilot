import { motion } from "motion/react";
import { useEffect, useState } from "react";

interface BlurTextProps {
  text: string;
  delay?: number;
  className?: string;
  animateBy?: "words" | "letters";
  direction?: "top" | "bottom";
}

export default function BlurText({
  text,
  delay = 0,
  className = "",
  animateBy = "words",
  direction = "top",
}: BlurTextProps) {
  const elements = animateBy === "words" ? text.split(" ") : text.split("");

  return (
    <div className={`flex flex-wrap justify-center ${className}`}>
      {elements.map((el, i) => (
        <motion.span
          key={i}
          initial={{ filter: "blur(10px)", opacity: 0, y: direction === "top" ? -20 : 20 }}
          whileInView={{ filter: "blur(0px)", opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{
            duration: 0.8,
            delay: delay + i * 0.1,
            ease: "easeOut",
          }}
          className="inline-block mr-[0.25em]"
        >
          {el === " " ? "\u00A0" : el}
        </motion.span>
      ))}
    </div>
  );
}
