import {Music2, Film, Mic, UserCircle, Languages, Sparkles, MapPin, Calendar, Globe} from "lucide-react";

const CARD_BG = "#59357E";

function FilterCard({ icon: Icon, label, image, small = false }) {
  return (
    <div
      className={`rounded-lg flex flex-col items-center justify-center cursor-pointer transition-all duration-200 hover:brightness-110 overflow-hidden ${
        small
          ? "h-[95px] p-2 gap-1"
          : "h-[120px] p-2.5 gap-1.5"
      }`}
      style={{
        backgroundImage: `
          linear-gradient(rgba(89,53,126,0.72), rgba(89,53,126,0.72)),
          url(${image})
        `,
        backgroundSize: "cover",
        backgroundPosition: "center",
      }}
    >
      <div
        className={`rounded-full flex items-center justify-center ${
          small ? "w-7 h-7" : "w-9 h-9"
        }`}
        style={{ background: "rgba(255,255,255,0.18)" }}
      >
        <Icon size={small ? 16 : 20} className="text-white" />
      </div>

      <p
        className={`text-white font-semibold text-center leading-tight ${
          small ? "text-[20px]" : "text-[20px]"
        }`}
      >
        {label}
      </p>
    </div>
  );
}

function SectionHeader({ label, icon: Icon }) {
  return (
    <div
      className="rounded-lg px-4 py-3 mb-2 flex items-center justify-center gap-2"
      style={{
        background:
          "linear-gradient(135deg, rgba(89,53,126,0.95), rgba(138,68,147,0.95))",
        boxShadow:
          "0 4px 15px rgba(89,53,126,0.3), inset 0 1px 0 rgba(255,255,255,0.1)",
      }}
    >
      <Icon size={18} className="text-white" />

      <span
        className="text-[15px] font-bold tracking-wider uppercase text-white"
        style={{ letterSpacing: "0.08em" }}
      >
        {label}
      </span>
    </div>
  );
}

export default function Panel() {
  return (
    <div className="w-[52%] min-h-0 overflow-y-auto no-scrollbar flex flex-col gap-2.5 flex-shrink-0 pr-1">

      {/* Song Filters */}
      <div>
        <SectionHeader label="Discover Songs By" icon={Music2} />

        <div className="grid grid-cols-3 gap-2">
          <FilterCard
            icon={UserCircle}
            label="Artist"
            image="https://images.unsplash.com/photo-1526218626217-dc65a29bb444?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&q=80&w=1080"
          />

          <FilterCard
            icon={Music2}
            label="Genre"
            image="https://images.unsplash.com/photo-1619983081593-e2ba5b543168?w=1080"
          />

          <FilterCard
            icon={Languages}
            label="Language"
            image="https://images.unsplash.com/photo-1512076249812-fd58fb2c8748?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&q=80&w=1080"
          />
        </div>
      </div>

      {/* Movie Filters */}
      <div className="flex flex-col">
        <SectionHeader label="Discover Movies By" icon={Film} />

        <div className="grid grid-cols-3 gap-2">

          <FilterCard
            icon={UserCircle}
            label="Actor"
            image="https://images.unsplash.com/photo-1503095396549-807759245b35?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&q=80&w=1080"
          />

          <FilterCard
            icon={Film}
            label="Director"
            image="https://images.unsplash.com/photo-1489599849927-2ee91cede3ba?q=80&w=1080"
          />

          <FilterCard
            icon={Sparkles}
            label="Genre"
            image="https://images.unsplash.com/photo-1440404653325-ab127d49abc1?q=80&w=1080"
          />

          <FilterCard
            icon={MapPin}
            label="Country"
            image="https://images.unsplash.com/photo-1521295121783-8a321d551ad2?q=80&w=1080"
          />

          <FilterCard
            icon={Calendar}
            label="Year"
            image="https://images.unsplash.com/photo-1723396612574-961649793bb9?w=400"
          />

          <FilterCard
            icon={Languages}
            label="Language"
            image="https://images.unsplash.com/photo-1512076249812-fd58fb2c8748?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&q=80&w=1080"
          />
        </div>
      </div>

      {/* Supported Languages */}
      <div>
        <SectionHeader
          label="Chatbot Supported Languages"
          icon={Globe}
        />

        <div className="grid grid-cols-2 gap-2">

          {/* Text Chat */}
          <div
            className="rounded-lg p-2.5 h-[90px] flex flex-col items-center justify-center gap-1.5 cursor-pointer"
            style={{ background: CARD_BG }}
          >
            <div className="flex gap-1">
              <div className="w-10 h-10 rounded-full flex items-center justify-center text-[13px] font-bold bg-white/15 text-white">
                EN
              </div>

              <div className="w-10 h-10 rounded-full flex items-center justify-center text-[13px] font-bold bg-white/15 text-white">
                MY
              </div>
            </div>

            <p className="text-white text-[15px] font-semibold">
              Text Chat
            </p>
          </div>

          {/* Voice Input */}
          <div
            className="rounded-lg p-2.5 h-[90px] flex flex-col items-center justify-center gap-1.5 cursor-pointer"
            style={{ background: CARD_BG }}
          >
            <div className="w-10 h-10 rounded-full flex items-center justify-center text-[13px] font-bold bg-white/15 text-white">
              EN
            </div>

            <p className="text-white text-[15px] font-semibold">
              Voice Input
            </p>
          </div>

        </div>
      </div>
    </div>
  );
}