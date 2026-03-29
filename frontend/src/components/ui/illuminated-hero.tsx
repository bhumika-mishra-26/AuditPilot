import React, { useEffect, useRef } from 'react';
import { cn } from '../../lib/utils';
import gsap from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';
import SplitType from 'split-type';

gsap.registerPlugin(ScrollTrigger);

export function IlluminatedHero() {
	const heroRef = useRef<HTMLDivElement>(null);
	const line1Ref = useRef<HTMLDivElement>(null);
	const line2Ref = useRef<HTMLSpanElement>(null);
	const line3Ref = useRef<HTMLDivElement>(null);
	const subtextRef = useRef<HTMLParagraphElement>(null);
	const topCircleRef = useRef<HTMLDivElement>(null);
	const bottomCircleRef = useRef<HTMLDivElement>(null);

	useEffect(() => {
		const topCircle = topCircleRef.current;
		const bottomCircle = bottomCircleRef.current;
		const hero = heroRef.current;
		if (!topCircle || !bottomCircle || !hero) return;

		// ── 1. CIRCLES: FLY IN FROM TOP & BOTTOM ON LOAD ──
		gsap.fromTo(topCircle,
			{ y: '-150%', opacity: 0 },
			{ y: '-70%', opacity: 1, duration: 2, ease: 'power4.out', delay: 0.1 }
		);
		gsap.fromTo(bottomCircle,
			{ y: '150%', opacity: 0 },
			{ y: '70%', opacity: 1, duration: 2, ease: 'power4.out', delay: 0.1 }
		);

		// ── 2. TEXT: FULLY VISIBLE ON LOAD, CHAR-BY-CHAR EXIT ON SCROLL ──
		const lines = [line1Ref.current, line2Ref.current, line3Ref.current].filter(Boolean) as HTMLElement[];
		const splits: SplitType[] = [];
		const allChars: Element[] = [];

		lines.forEach((el) => {
			const s = new SplitType(el, { types: 'chars', tagName: 'span' });
			splits.push(s);
			if (s.chars) allChars.push(...s.chars);
		});

		// Start fully visible — no entry animation
		gsap.set(allChars, { opacity: 1, y: 0, scale: 1, filter: 'blur(0px)' });

		// As hero scrolls off screen, chars blur/fade/drop OUT — last char exits first (reversed stagger)
		gsap.to(allChars, {
			opacity: 0,
			y: 40,
			scale: 0.92,
			filter: 'blur(12px)',
			ease: 'power2.in',
			stagger: { each: 0.04, from: 'end' },
			scrollTrigger: {
				trigger: hero,
				start: 'top top',
				end: '+=350',
				scrub: 0.5,
			},
		});

		// Subtext fades out earlier
		if (subtextRef.current) {
			gsap.to(subtextRef.current, {
				opacity: 0,
				y: 20,
				scrollTrigger: {
					trigger: hero,
					start: 'top top',
					end: '30% top',
					scrub: 1,
				},
			});
		}

		// ── 3. CIRCLES: STRICTLY SIDEWAYS PARALLAX ON SCROLL ──
		gsap.to(topCircle, {
			x: -300,
			ease: 'none',
			scrollTrigger: {
				trigger: hero,
				start: 'top top',
				end: 'bottom top',
				scrub: true,
			},
		});
		gsap.to(bottomCircle, {
			x: 300,
			ease: 'none',
			scrollTrigger: {
				trigger: hero,
				start: 'top top',
				end: 'bottom top',
				scrub: true,
			},
		});

		return () => {
			splits.forEach(s => s.revert());
			ScrollTrigger.getAll().forEach(t => t.kill());
		};
	}, []);

	const circleStyle: React.CSSProperties = {
		boxShadow: `
			inset 0 0 60px 10px rgba(99, 102, 241, 0.4),
			inset 0 0 150px 40px rgba(124, 58, 237, 0.15),
			0 0 80px 20px rgba(99, 102, 241, 0.25),
			0 0 160px 60px rgba(79, 70, 229, 0.12)
		`,
		border: '1.5px solid rgba(99, 102, 241, 0.35)',
	};

	return (
		<div
			ref={heroRef}
			className="relative w-full min-h-[120vh] flex flex-col items-center justify-center pt-32 pb-24 overflow-hidden bg-black text-white"
		>
			{/* Background circles */}
			<div className="absolute inset-0 flex items-center justify-center pointer-events-none overflow-hidden">
				<div className="relative w-[60%] h-[100vh]">
					{/* Top Circle */}
					<div
						ref={topCircleRef}
						className="absolute top-0 left-0 right-0 h-[95%] rounded-[100em] border-[1.5px] border-indigo-500/40 shadow-[0_0_80px_rgba(99,102,241,0.4)]"
						style={{ ...circleStyle, transform: 'translateY(-60%) scale(1.25)', transformOrigin: 'center center', willChange: 'transform' }}
					/>
					{/* Bottom Circle */}
					<div
						ref={bottomCircleRef}
						className="absolute bottom-0 left-0 right-0 h-[95%] rounded-[100em] border-[1.5px] border-indigo-500/40 shadow-[0_0_80px_rgba(99,102,241,0.4)]"
						style={{ ...circleStyle, transform: 'translateY(35%) scale(1.4)', transformOrigin: 'center center', willChange: 'transform' }}
					/>
				</div>
			</div>

			{/* Text content */}
			<div className="relative z-10 flex flex-col items-center gap-4 px-4 text-center">
				<div
					ref={line1Ref}
					className="text-4xl md:text-6xl lg:text-7xl font-semibold text-white leading-tight"
				>
					Introducing
				</div>

				<span
					ref={line2Ref}
					className="block text-4xl md:text-6xl lg:text-7xl font-bold leading-tight relative hero-glow-text"
					style={{ filter: 'url(#glow-4)' }}
				>
					AuditPilot
				</span>

				<div
					ref={line3Ref}
					className="text-4xl md:text-6xl lg:text-7xl font-semibold text-white leading-tight"
				>
					Command Center.
				</div>

				<p
					ref={subtextRef}
					className="mt-4 max-w-[28em] bg-gradient-to-t from-[#86868b] to-[#bdc2c9] bg-clip-text text-center font-semibold text-transparent px-4"
				>
					Monitor. Execute. Explain.{' '}
					<span className="relative inline-block font-black text-[#e0e7ff]">AI Operations</span>{' '}
					built for modern audit workflows at scale.
				</p>
			</div>
		</div>
	);
}
