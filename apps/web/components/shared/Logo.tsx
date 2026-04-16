import React from "react";

export function Logo({ size = 28 }: { size?: number }) {
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 32 32"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      aria-hidden
    >
      <defs>
        <linearGradient id="forgeops-grad" x1="0" y1="0" x2="32" y2="32" gradientUnits="userSpaceOnUse">
          <stop offset="0%" stopColor="#aa91ff" />
          <stop offset="100%" stopColor="#5a2feb" />
        </linearGradient>
      </defs>
      <rect x="2" y="2" width="28" height="28" rx="8" fill="url(#forgeops-grad)" opacity="0.18" />
      <path
        d="M8 22 L16 8 L24 22 M11 18 L21 18"
        stroke="url(#forgeops-grad)"
        strokeWidth="2.2"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
      <circle cx="16" cy="8" r="1.6" fill="#aa91ff" />
    </svg>
  );
}
