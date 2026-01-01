export const websocketService = {
  connect: (url: string) => {
    // Placeholder implementation
    console.log(`Connecting to WebSocket at ${url}`);
  },
  disconnect: () => {
    console.log('Disconnecting WebSocket');
  },
  on: (_event: string, _callback: Function) => {
    // Placeholder
  }
};
