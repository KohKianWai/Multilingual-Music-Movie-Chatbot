import React from "react";
import Panel from "./pages/Panel";
import Chatbot from "./pages/Chatbot";
import musebotLogo from "./assets/images/musebottlogo.png";

export default function App() {
  return (
    <div
      className="h-screen flex flex-col overflow-hidden"
      style={{
        fontFamily: "'Outfit', system-ui, sans-serif",
        backgroundImage: `
          linear-gradient(
            135deg,
            rgba(109,40,217,0.50),
            rgba(38, 14, 41, 0.5),
            rgba(192,38,211,0.30)
          ),
          url("https://images.unsplash.com/photo-1540039155733-5bb30b53aa14?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&q=80&w=1080")
        `,
        backgroundSize: "cover",
        backgroundPosition: "center",
      }}
    >
      {/* Film Reel Styles */}
      <style>{`
        .film-reel {
          position: relative;
          background: linear-gradient(135deg, rgba(89,53,126,0.95), rgba(138,68,147,0.95));
          height: 12px;
          overflow: hidden;
        }

        .film-reel::before {
          content: '';
          position: absolute;
          top: 50%;
          left: 0;
          right: 0;
          height: 1px;
          background: #7C3AED;
          transform: translateY(-50%);
        }

        .film-holes {
          position: absolute;
          inset: 0;
          background-image:
            radial-gradient(circle at center, #C4B5FD 3px, transparent 3px);
          background-size: 16px 12px;
          background-position: 8px center;
        }
      `}</style>

      {/* Navbar Section */}
      <div className="flex-shrink-0 relative z-10">

        {/* Top Film Reel */}
        <div className="film-reel">
          <div className="film-holes" />
        </div>

        {/* Navbar */}
        <nav
          className="h-20 flex items-center justify-center px-6 shadow-lg"
          style={{
            background:
              "linear-gradient(to bottom, rgba(240,235,250,0.95), rgba(240,235,250,0.75))",
            backdropFilter: "blur(15px)",
            WebkitBackdropFilter: "blur(15px)",
            boxShadow: "0 4px 20px rgba(123,44,191,0.15)",
          }}
        >
          <div className="flex flex-col items-center gap-1">
            <img
              src={musebotLogo}
              alt="MuseBot Logo"
              className="h-10 object-contain"
            />

            <span className="text-xs text-gray-700 tracking-wide">
              Your Music & Movie Recommendation Chatbot
            </span>
          </div>
        </nav>

        {/* Bottom Film Reel */}
        <div className="film-reel">
          <div className="film-holes" />
        </div>

      </div>

      {/* Main Layout */}
      <div className="flex-1 flex p-5 gap-5 min-h-0 overflow-hidden">
        <Panel />
        <Chatbot />
      </div>
    </div>
  );
}