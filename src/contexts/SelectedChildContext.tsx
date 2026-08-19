import React, { createContext, useContext, useMemo, useState } from "react";
import { Child, CHILDREN } from "../data/parentMock";

type SelectedChildContextValue = {
  childrenList: Child[];
  selectedChild: Child;
  selectedId: string;
  setSelectedId: (id: string) => void;
};

const SelectedChildContext = createContext<SelectedChildContextValue | null>(
  null
);

export function SelectedChildProvider({
  children,
}: {
  children: React.ReactNode;
}) {
  const [selectedId, setSelectedId] = useState(CHILDREN[0].id);

  const value = useMemo(() => {
    const selectedChild =
      CHILDREN.find((child) => child.id === selectedId) ?? CHILDREN[0];

    return {
      childrenList: CHILDREN,
      selectedChild,
      selectedId,
      setSelectedId,
    };
  }, [selectedId]);

  return (
    <SelectedChildContext.Provider value={value}>
      {children}
    </SelectedChildContext.Provider>
  );
}

export function useSelectedChild() {
  const context = useContext(SelectedChildContext);
  if (!context) {
    throw new Error("useSelectedChild must be used within SelectedChildProvider");
  }
  return context;
}
