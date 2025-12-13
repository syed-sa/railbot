import React from 'react';

export const Button = ({ 
  onClick, 
  disabled, 
  variant = 'primary', 
  className = '',
  type = 'button',
  ...props 
}) => {
  const baseClasses = 'px-6 py-3 rounded-lg font-medium transition-colors disabled:cursor-not-allowed';
  
  const variants = {
    primary: 'bg-indigo-600 text-white hover:bg-indigo-700 disabled:bg-indigo-400',
    secondary: 'bg-gray-100 text-gray-600 hover:bg-gray-200 disabled:bg-gray-50',
    danger: 'bg-red-600 text-white hover:bg-red-700 disabled:bg-red-400',
  };

  // Combine base, variant, and custom classes
  const buttonClasses = `${baseClasses} ${variants[variant]} ${className}`;

  return (
    // 1. Missing <button> tag added here
    <button
      onClick={onClick}
      disabled={disabled}
      type={type}
      className={buttonClasses} // 2. Apply the dynamically computed classes
      {...props} // 3. Spread any other remaining props (e.g., aria-label, etc.)
    >
    </button>
  );
};