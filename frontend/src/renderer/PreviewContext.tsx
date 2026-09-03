import React, { createContext, useState, ReactNode } from 'react';

interface PreviewContextType {
  isPreviewMode: boolean;
  togglePreviewMode: () => void;
}

const PreviewContext = createContext<PreviewContextType | undefined>(undefined);

export const PreviewProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [isPreviewMode, setIsPreviewMode] = useState(false);

  const togglePreviewMode = () => setIsPreviewMode((prev) => !prev);

  return (
    <PreviewContext.Provider value={{ isPreviewMode, togglePreviewMode }}>
      {children}
    </PreviewContext.Provider>
  );
};

