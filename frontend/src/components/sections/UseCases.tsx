import { Landmark, ShieldCheck, Terminal, Building2 } from "lucide-react";
import ElectricBorder from "../ui/ElectricBorder";
import { motion } from "motion/react";

export const UseCases = () => {
  const cases = [
    {
      title: 'Finance Auditing',
      description: 'Detect fraudulent transactions and ensure regulatory compliance in real-time.',
      icon: Landmark,
      image: 'https://images.unsplash.com/photo-1551288049-bebda4e38f71?auto=format&fit=crop&q=80&w=800',
      color: "rgb(6, 182, 212)",
      filter: "turbulent-displace-teal"
    },
    {
      title: 'Fraud Detection',
      description: 'Identify suspicious patterns and prevent financial loss before it happens.',
      icon: ShieldCheck,
      image: 'https://images.unsplash.com/photo-1563986768609-322da13575f3?auto=format&fit=crop&q=80&w=800',
      color: "rgb(245, 158, 11)",
      filter: "turbulent-displace-amber"
    },
    {
      title: 'Cybersecurity Logs',
      description: 'Monitor system logs for unauthorized access and potential security breaches.',
      icon: Terminal,
      image: 'https://images.unsplash.com/photo-1550751827-4bd374c3f58b?auto=format&fit=crop&q=80&w=800',
      color: "rgb(139, 92, 246)",
      filter: "turbulent-displace-purple"
    },
    {
      title: 'Enterprise Monitoring',
      description: 'Holistic visibility across all departments and business processes.',
      icon: Building2,
      image: 'https://images.unsplash.com/photo-1486406146926-c627a92ad1ab?auto=format&fit=crop&q=80&w=800',
      color: "rgb(20, 184, 166)",
      filter: "turbulent-displace-teal"
    }
  ];

  return (
    <section id="use-cases" className="py-24">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-16">
          <h2 className="text-3xl md:text-5xl font-bold text-white mb-4">Industry Use Cases</h2>
          <p className="text-gray-400">Tailored solutions for every sector.</p>
        </div>

        <motion.div 
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true, margin: "-100px" }}
          variants={{ visible: { transition: { staggerChildren: 0.15 } } }}
          className="grid md:grid-cols-2 gap-12 px-4"
        >
          {cases.map((item) => (
            <motion.div 
              key={item.title}
              variants={{
                hidden: { opacity: 0, y: 40 },
                visible: { opacity: 1, y: 0, transition: { type: "spring", stiffness: 100, damping: 20 } }
              }}
            >
              <ElectricBorder color={item.color} className="h-full bg-black text-left">
                <div className="relative overflow-hidden rounded-3xl h-80 text-left">
                  <img 
                    src={item.image} 
                    alt={item.title}
                    className="absolute inset-0 w-full h-full object-cover opacity-40 group-hover:scale-110 transition-transform duration-700"
                    referrerPolicy="no-referrer"
                  />
                  <div className="absolute inset-0 bg-gradient-to-t from-black via-black/50 to-transparent" />
                  <div className="absolute bottom-0 left-0 p-8 text-left text-white w-full">
                    <div className="w-12 h-12 rounded-xl flex items-center justify-center mb-4" style={{ backgroundColor: item.color }}>
                      <item.icon className="w-6 h-6 text-white" />
                    </div>
                    <h3 className="text-2xl font-bold text-white mb-2">{item.title}</h3>
                    <p className="text-gray-400 max-w-sm">{item.description}</p>
                  </div>
                </div>
              </ElectricBorder>
            </motion.div>
          ))}
        </motion.div>
      </div>
    </section>
  );
};
