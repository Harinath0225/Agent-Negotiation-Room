import React, { createContext, useContext, useState, ReactNode } from 'react';

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

export const usePreview = () => {
  const context = useContext(PreviewContext);
  if (!context) {
    throw new Error('usePreview must be used within a PreviewProvider');
  }
  return context;
};
