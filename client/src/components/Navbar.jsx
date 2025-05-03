import { FiMenu, FiX } from "react-icons/fi";

export default function Navbar({ onMenuClick, isSidebarOpen }) {
  return (
    <nav className="bg-white shadow-sm">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          <div className="flex items-center">
            <button
              onClick={onMenuClick}
              className="p-2 rounded-lg text-gray-600 hover:bg-gray-100 focus:outline-none"
            >
              {isSidebarOpen ? (
                <FiX className="h-6 w-6" />
              ) : (
                <FiMenu className="h-6 w-6" />
              )}
            </button>
            <div className="ml-4 flex items-center">
              <span className="text-xl font-semibold text-gray-800">
                Clinical ChatBot
              </span>
            </div>
          </div>
        </div>
      </div>
    </nav>
  );
}
