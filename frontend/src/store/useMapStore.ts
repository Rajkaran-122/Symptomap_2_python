/*
 * Map State Management
 */

import { create } from 'zustand';

interface MapState {
  viewState: {
    latitude: number;
    longitude: number;
    zoom: number;
  };
  setViewState: (viewState: MapState['viewState']) => void;
}

export const useMapStore = create<MapState>((set) => ({
  viewState: {
    latitude: 19.0760,
    longitude: 72.8777,
    zoom: 11
  },
  setViewState: (newViewState) => set({ viewState: newViewState })
}));
