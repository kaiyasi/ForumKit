import { Outlet } from "react-router-dom";
import Header from "./Header";
import Footer from "./Footer";
import { cn } from "../lib/utils";

const Layout = () => {
  return (
    <div className={cn(
      "min-h-screen flex flex-col",
      "bg-background text-foreground",
      "bg-[radial-gradient(ellipse_80%_80%_at_50%_-20%,rgba(120,119,198,0.3),rgba(255,255,255,0))]]",
      "dark:bg-[radial-gradient(ellipse_80%_80%_at_50%_-20%,rgba(120,119,198,0.3),rgba(255,255,255,0))]]"
    )}>
      <Header />
      <main className="flex-grow container mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <Outlet />
      </main>
      <Footer />
    </div>
  );
};

export default Layout;