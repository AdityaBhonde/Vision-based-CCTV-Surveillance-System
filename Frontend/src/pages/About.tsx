import { Navigation } from "@/components/ui/navigation";
import { About as AboutSection } from "@/components/About";

const About = () => {
  return (
    <div className="min-h-screen bg-background">
      <Navigation />
      <AboutSection />
    </div>
  );
};

export default About;