export const Input = ({
  label,
  error,
  className = '',
  ...props
}) => {
  const inputId =
    props.id || `input-${label ? label.replace(/\s/g, '-') : Math.random()}`;

  return (
    <div className={`flex flex-col ${className}`}>
      
      {label && (
        <label
          htmlFor={inputId}
          className="text-sm font-medium text-gray-700 mb-2"
        >
          {label}
        </label>
      )}

      <input
        id={inputId}
        className={`w-full px-4 py-2 rounded-lg border focus:outline-none focus:ring-2 focus:ring-indigo-500 ${
          error ? 'border-red-500' : 'border-gray-300'
        }`}
        {...props}
      />

      {error && (
        <p className="mt-1 text-sm text-red-600">
          {error}
        </p>
      )}
    </div>
  );
};
