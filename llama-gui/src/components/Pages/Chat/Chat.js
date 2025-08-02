import { ChatInterface, ChatProvider } from './';

const Chat = () => {
  return (
    <ChatProvider>
      <ChatInterface />
    </ChatProvider>
  );
};

export default Chat;
