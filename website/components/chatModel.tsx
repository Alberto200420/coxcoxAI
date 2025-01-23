"use client";

import { useState, useEffect } from "react";
import {
  Dialog,
  DialogBackdrop,
  DialogPanel,
  DialogTitle,
  TransitionChild,
} from "@headlessui/react";

interface ModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export default function ChatModel({ isOpen, onClose }: ModalProps) {
  const [messages, setMessages] = useState([
    { id: 1, text: "¡Hola! ¿En qué puedo ayudarte?", isBot: true },
  ]);
  const [newMessage, setNewMessage] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [uuid, setUUID] = useState<string>("");

  function generateRandomInt(): string {
    return Math.floor(Math.random() * 1_000_000_0000).toString();
  }

  useEffect(() => {
    const newRandomInt = generateRandomInt();
    setUUID(newRandomInt);
  }, []);

  const handleSend = async (e: any) => {
    e.preventDefault();
    if (newMessage.trim() === "") return;

    // Add user message
    const userMessage = {
      id: messages.length + 1,
      text: newMessage,
      isBot: false,
    };

    setMessages((prev) => [...prev, userMessage]);
    setNewMessage("");
    setIsLoading(true);
    try {
      const response = await fetch(
        "https://j3v6oi2w3pktz75kwmltgmkrpa0mguat.lambda-url.us-east-1.on.aws/",
        {
          method: "POST",
          body: JSON.stringify({ text: newMessage, thread_id: uuid }),
        }
      );
      const responseData = await response.text();
      setIsLoading(false);
      const botMessage = {
        id: messages.length + 2,
        text: responseData,
        isBot: true,
      };

      setMessages((prev) => [...prev, botMessage]);
    } catch (error) {
      // Add error message
      setIsLoading(false);
      const errorMessage = {
        id: messages.length + 2,
        text: "Lo siento, hubo un problema al procesar tu mensaje. Intenta nuevamente más tarde.",
        isBot: true,
      };

      setMessages((prev) => [...prev, errorMessage]);
    }
  };

  return (
    <Dialog open={isOpen} onClose={onClose} className="relative z-10">
      <DialogBackdrop
        transition
        className="fixed inset-0 bg-gray-500/75 transition-opacity duration-500 ease-in-out data-[closed]:opacity-0"
      />

      <div className="fixed inset-0 overflow-hidden">
        <div className="absolute inset-0 overflow-hidden">
          <div className="pointer-events-none fixed inset-y-0 right-0 flex max-w-full pl-10">
            <DialogPanel
              transition
              className="pointer-events-auto relative w-screen max-w-md transform transition duration-500 ease-in-out data-[closed]:translate-x-full sm:duration-700"
            >
              <TransitionChild>
                <div className="absolute left-0 top-0 -ml-8 flex pr-2 pt-4 duration-500 ease-in-out data-[closed]:opacity-0 sm:-ml-10 sm:pr-4">
                  <button
                    type="button"
                    onClick={() => onClose}
                    className="relative rounded-md text-gray-300 hover:text-white focus:outline-none focus:ring-2 focus:ring-white"
                  >
                    <span className="sr-only">Cerrar panel</span>
                  </button>
                </div>
              </TransitionChild>
              <div className="flex h-full flex-col overflow-y-scroll bg-white py-6 shadow-xl">
                <div className="px-4 sm:px-6">
                  <DialogTitle className="text-base font-semibold text-gray-900">
                    Escribe las dudas que tengas sobre nuestro servicio. Nuestro
                    agente de IA te responderá
                  </DialogTitle>
                </div>
                <div className="relative mt-6 flex-1 px-4 sm:px-6">
                  <div className="flex flex-col h-full">
                    <div className="flex-1 overflow-y-auto p-4 space-y-4">
                      {messages.map((message) => (
                        <div
                          key={message.id}
                          className={`flex ${
                            message.isBot ? "justify-start" : "justify-end"
                          }`}
                        >
                          <div
                            className={`max-w-[80%] rounded-2xl px-4 py-2 ${
                              message.isBot
                                ? "bg-gray-100 text-gray-900"
                                : "bg-blue-600 text-white"
                            }`}
                          >
                            <p className="text-sm">{message.text}</p>
                          </div>
                        </div>
                      ))}
                      {isLoading && (
                        <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-gray-900"></div>
                      )}
                    </div>

                    <form onSubmit={handleSend} className="border-t p-4">
                      <div className="flex space-x-4">
                        <input
                          type="text"
                          value={newMessage}
                          onChange={(e) => setNewMessage(e.target.value)}
                          placeholder="Escribe tu mensaje aquí..."
                          className="flex-1 rounded-full border border-gray-300 px-4 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
                        />
                        <button
                          type="submit"
                          className="rounded-full bg-blue-600 px-6 py-2 text-sm font-semibold text-white hover:bg-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
                        >
                          Enviar
                        </button>
                      </div>
                    </form>
                  </div>
                </div>
              </div>
            </DialogPanel>
          </div>
        </div>
      </div>
    </Dialog>
  );
}
