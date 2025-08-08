import { Link } from "react-router-dom";
import Navbar from "./Navbar";
import { ModeToggle } from "./ModeToggle";

const Header = () => {
  return (
    <header className="sticky top-0 z-50 w-full border-b border-border/40 bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <div className="container mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          <Link to="/" className="text-xl font-bold text-foreground/90 hover:text-foreground transition-colors">
            ForumKit
          </Link>
          <div className="flex items-center gap-4">
            <Navbar />
            <ModeToggle />
          </div>
        </div>
      </div>
    </header>
  );
};

export default Header;
