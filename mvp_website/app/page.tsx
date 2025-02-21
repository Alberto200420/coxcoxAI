"use client";
import ChatModel from "@/components/chatModel";
import { useState } from "react";

export default function Home() {
  const [open, setIsModalOpen] = useState(false);
  const closeModal = () => setIsModalOpen(false);
  return (
    <div>
      <main className="max-w-screen-xl mx-auto p-10 grid grid-cols-1 md:grid-cols-2 gap-10 flex-1">
        <div className="space-y-6">
          <h1 className="text-4xl font-bold leading-tight text-black">
            Reemplaza tu equipo de telemarketing con el agente de inteligencia
            artificial Coxcox AI
          </h1>

          <p className="text-lg text-gray-800">
            El agente está diseñado para realizar el trabajo de telemarketing
            ayudando a los clientes con las siguientes tareas:
          </p>

          <ul className="">
            <li className="pl-5 relative before:content-['•'] before:absolute before:left-0 before:text-black">
              Atender sus consultas
            </li>
            <li className="pl-5 relative before:content-['•'] before:absolute before:left-0 before:text-black">
              Brindar soporte
            </li>
            <li className="pl-5 relative before:content-['•'] before:absolute before:left-0 before:text-black">
              Tomar pedidos de los clientes
            </li>
            <li className="pl-5 relative before:content-['•'] before:absolute before:left-0 before:text-black">
              Ingresar pedidos a la base de datos de la empresa en la que está
              trabajando el agente de inteligencia artificial
            </li>
            <li className="pl-5 relative before:content-['•'] before:absolute before:left-0 before:text-black">
              Obtener información sobre los productos de la empresa
            </li>
            <li className="pl-5 relative before:content-['•'] before:absolute before:left-0 before:text-black">
              Solicitar estados de pedidos
            </li>
          </ul>
        </div>

        <div>
          <div className="relative w-full pb-[56.25%] h-0 overflow-hidden">
            <iframe
              src="https://www.youtube.com/embed/JqEQ100Dd0w?si=-_f40wnZU4nEMh6g"
              title="YouTube video player"
              allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
              className="absolute top-0 left-0 w-full h-full border-0"
            ></iframe>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-5 mt-10">
            <a
              href="mailto:albertog1meza@gmail.com"
              className="flex flex-col items-center text-center p-4 bg-white border border-gray-300 rounded-lg text-gray-700 hover:-translate-y-1 hover:shadow-lg transition-transform"
            >
              <svg
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="2"
                className="w-10 h-10 mb-2"
              >
                <rect x="3" y="5" width="18" height="14" rx="2" />
                <polyline points="3 7 12 13 21 7" />
              </svg>
              contactame
            </a>
            <button
              onClick={() => setIsModalOpen(true)}
              className="flex flex-col items-center text-center p-4 bg-white border border-gray-300 rounded-lg text-gray-700 hover:-translate-y-1 hover:shadow-lg transition-transform"
            >
              <svg
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="2"
                className="w-10 h-10 mb-2"
              >
                <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2v10z" />
              </svg>
              Contacta con mi agente
            </button>
          </div>
        </div>
      </main>
      <ChatModel isOpen={open} onClose={closeModal} />
      <footer className="p-5 text-center mt-auto">
        &copy; 2025 COXCOX AI. Todos los derechos reservados.
      </footer>
    </div>
  );
}
