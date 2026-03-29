import { Layout, Zap, BarChart3, Shield } from "lucide-react";
import WavyCard from "../ui/WavyCard";
import { motion } from "motion/react";

export const Features = () => {
  const features = [
    { title: "Audit Workflow Management", desc: "Streamline your entire audit lifecycle from planning to execution with automated task routing.", icon: Layout, color: "rgb(6, 182, 212)", filter: "turbulent-displace-teal" },
    { title: "Real-time Monitoring", desc: "Get instant visibility into ongoing audits with live status updates and bottleneck detection.", icon: Zap, color: "rgb(139, 92, 246)", filter: "turbulent-displace-purple" },
    { title: "Data Visualization", desc: "Transform complex audit logs into actionable insights with interactive charts and heatmaps.", icon: BarChart3, color: "rgb(245, 158, 11)", filter: "turbulent-displace-amber" },
    { title: "Role-based Access", desc: "Secure your sensitive data with granular permissions and enterprise-grade authentication.", icon: Shield, color: "rgb(20, 184, 166)", filter: "turbulent-displace-teal" },
  ];

  return (
    <section id="features" className="py-24">
      <div className="max-w-7xl mx-auto px-6">
        <div className="text-center mb-20">
          <h2 className="text-4xl font-bold text-white mb-4 font-heading">Core Features</h2>
          <p className="text-gray-400 max-w-2xl mx-auto">Everything you need to manage modern audit workflows at scale.</p>
        </div>

        <motion.div 
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true, margin: "-100px" }}
          variants={{
            visible: { transition: { staggerChildren: 0.1 } }
          }}
          className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-8"
        >
          {features.map((f, i) => (
            <motion.div 
              key={i}
              variants={{
                hidden: { opacity: 0, y: 30 },
                visible: { opacity: 1, y: 0, transition: { type: "spring", stiffness: 100, damping: 20 } }
              }}
              className="h-full"
            >
              <WavyCard color={f.color} filterId={f.filter} containerClassName="h-full" className="p-8 bg-black/60 h-full">
                <div className="w-12 h-12 bg-white/5 rounded-xl flex items-center justify-center mb-6 border border-white/10">
                  <f.icon className="w-6 h-6" style={{ color: f.color }} />
                </div>
                <h3 className="text-xl font-bold text-white mb-3">{f.title}</h3>
                <p className="text-gray-400 leading-relaxed">{f.desc}</p>
              </WavyCard>
            </motion.div>
          ))}
        </motion.div>
      </div>
    </section>
  );
};
