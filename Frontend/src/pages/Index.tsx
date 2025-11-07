import { Navigation } from "@/components/ui/navigation";
import { Hero } from "@/components/Hero";
import { Features } from "@/components/Features";
import { TechStack } from "@/components/TechStack";

const Index = () => {
  return (
    <div className="min-h-screen bg-background">
      <Navigation />
      <main>
        <Hero />
        <Features />
        <TechStack />
      </main>
    </div>
  );
};

export default Index;
