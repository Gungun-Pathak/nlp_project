import {
  FiHome,
  FiPlusSquare,
  FiSave,
  FiSettings,
  FiBookOpen,
  FiX,
} from "react-icons/fi";

export default function Sidebar({ onClose, startNewChat }) {
  const menuItems = [
    { icon: FiHome, text: "Home", action: onClose },
    {
      icon: FiPlusSquare,
      text: "New Chat",
      action: () => {
        startNewChat();
        onClose();
      },
    },
    { icon: FiSave, text: "Saved Chats", action: onClose },
    { icon: FiSettings, text: "Settings", action: onClose },
    { icon: FiBookOpen, text: "Clinical Blogs", action: onClose },
  ];

  return (
    <div className="h-full flex flex-col">
      <div className="p-4 border-b border-gray-200 flex justify-between items-center">
        <h2 className="text-lg font-semibold text-gray-800">Menu</h2>
        <button
          onClick={onClose}
          className="p-1 hover:bg-gray-100 rounded-lg text-gray-600"
        >
          <FiX className="h-5 w-5" />
        </button>
      </div>

      <div className="flex-1 overflow-y-auto p-4">
        <nav className="space-y-2">
          <div className="mb-6">
            <h3 className="text-xs font-semibold text-gray-500 uppercase mb-2">
              Navigation
            </h3>
            <ul className="space-y-1">
              {menuItems.map((item, index) => (
                <li key={index}>
                  <button
                    onClick={item.action}
                    className="w-full flex items-center p-2 text-gray-700 hover:bg-gray-100 rounded-lg transition-colors"
                  >
                    <item.icon className="h-5 w-5 mr-3 text-gray-600" />
                    <span className="text-sm">{item.text}</span>
                  </button>
                </li>
              ))}
            </ul>
          </div>

          <div>
            <h3 className="text-xs font-semibold text-gray-500 uppercase mb-2">
              Resources
            </h3>
            <ul className="space-y-1">
              <li>
                <button className="w-full flex items-center p-2 text-gray-700 hover:bg-gray-100 rounded-lg transition-colors">
                  <FiBookOpen className="h-5 w-5 mr-3 text-gray-600" />
                  <span className="text-sm">Research Papers</span>
                </button>
              </li>
            </ul>
          </div>
        </nav>
      </div>

      <div className="p-4 border-t border-gray-200">
        <p className="text-xs text-gray-500 text-center"></p>
      </div>
    </div>
  );
}
