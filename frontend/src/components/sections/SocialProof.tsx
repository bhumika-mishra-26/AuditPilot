import ScrollVelocity from "../ui/ScrollVelocity";

export const SocialProof = () => {
  return (
    <section className="py-12 border-y border-white/5 bg-white/2">
      <div className="max-w-[100vw] mx-auto overflow-hidden">
        <p className="text-center text-sm font-bold text-gray-600 uppercase tracking-widest mb-10">Used by modern teams</p>
        <div className="opacity-40 grayscale hover:grayscale-0 transition-all duration-700">
          <ScrollVelocity
            texts={["ACME        GLOBEX        SOYLENT        INITECH        UMBRELLA        "]}
            velocity={50}
            className="text-4xl md:text-5xl font-black text-white px-6 whitespace-pre"
            parallaxClassName="py-2"
          />
        </div>
      </div>
    </section>
  );
};
