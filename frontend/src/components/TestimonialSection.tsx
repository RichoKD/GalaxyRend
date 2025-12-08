"use client";

import AutoScroll from "embla-carousel-auto-scroll";
import { useRef } from "react";

import { Avatar, AvatarImage } from "@/components/ui/avatar";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import {
  Carousel,
  CarouselContent,
  CarouselItem,
} from "@/components/ui/carousel";

const testimonials1 = [
  {
    name: "Bill The Gamer-chan",
    role: "Creator",
    avatar:
      "https://deifkwefumgah.cloudfront.net/shadcnblocks/block/avatar-1.webp",
    content:
      "FluxFrame revolutionized my workflow. Post jobs, find talent fast, and results are top-notch.",
  },
  {
    name: "Sarah Kim",
    role: "Node",
    avatar:
      "https://deifkwefumgah.cloudfront.net/shadcnblocks/block/avatar-2.webp",
    content:
      "Finding quality work has never been easier. The platform is intuitive and payments are secure.",
  },
  {
    name: "Rico Kadma",
    role: "Admin",
    avatar:
      "https://deifkwefumgah.cloudfront.net/shadcnblocks/block/avatar-3.webp",
    content:
      "Managing disputes and overseeing the ecosystem is seamless with FluxFrame's admin tools.",
  },
  {
    name: "Dinah Macaulay",
    role: "Creator",
    avatar:
      "https://deifkwefumgah.cloudfront.net/shadcnblocks/block/avatar-4.webp",
    content:
      "The quality of work submissions exceeded expectations. Perfect for content creators like me.",
  },
  {
    name: "Jordan Lee",
    role: "Node",
    avatar:
      "https://deifkwefumgah.cloudfront.net/shadcnblocks/block/avatar-5.webp",
    content:
      "Transparent processes and fair rewards make FluxFrame my go-to platform for freelance work.",
  },
  {
    name: "Ryan Park",
    role: "Admin",
    avatar:
      "https://deifkwefumgah.cloudfront.net/shadcnblocks/block/avatar-6.webp",
    content:
      "The dispute resolution system is brilliant. Side-by-side comparisons make decisions clear.",
  },
];
const testimonials2 = [
  {
    name: "Lisa Wang",
    role: "Creator",
    avatar:
      "https://deifkwefumgah.cloudfront.net/shadcnblocks/block/avatar-1.webp",
    content:
      "Decentralized hiring at its finest. Smart contracts ensure everyone gets paid fairly.",
  },
  {
    name: "Carlos Ruiz",
    role: "Node",
    avatar:
      "https://deifkwefumgah.cloudfront.net/shadcnblocks/block/avatar-2.webp",
    content:
      "The AI analysis options help me submit better work. It's like having a quality checker.",
  },
  {
    name: "Anna Silva",
    role: "Admin",
    avatar:
      "https://deifkwefumgah.cloudfront.net/shadcnblocks/block/avatar-3.webp",
    content:
      "Platform moderation tools are comprehensive yet user-friendly. Great for maintaining quality.",
  },
  {
    name: "David Kim",
    role: "Creator",
    avatar:
      "https://deifkwefumgah.cloudfront.net/shadcnblocks/block/avatar-4.webp",
    content:
      "From posting jobs to reviewing submissions, everything flows smoothly on FluxFrame.",
  },
  {
    name: "Maya Patel",
    role: "Node",
    avatar:
      "https://deifkwefumgah.cloudfront.net/shadcnblocks/block/avatar-5.webp",
    content:
      "No middleman fees, direct payments, and genuine opportunities. This is the future of work.",
  },
  {
    name: "Tom Wilson",
    role: "Admin",
    avatar:
      "https://deifkwefumgah.cloudfront.net/shadcnblocks/block/avatar-6.webp",
    content:
      "System parameters are easy to adjust and the analytics dashboard provides great insights.",
  },
];

const TestimonialSection = () => {
  const plugin1 = useRef(
    AutoScroll({
      startDelay: 500,
      speed: 0.7,
    })
  );

  const plugin2 = useRef(
    AutoScroll({
      startDelay: 500,
      speed: 0.7,
      direction: "backward",
    })
  );
  return (
    <section className="relative py-20 md:py-32 max-w-7xl mx-auto px-6 overflow-hidden">
      <div className="container flex flex-col items-center gap-6 mb-16">
        <h2 className="text-4xl md:text-5xl font-bold text-center">
          Trusted by FluxFrame Community
        </h2>
        <p className="text-center text-lg md:text-xl text-slate-400 max-w-2xl">
          Decentralized work platform where Creators, Nodes, and Admins thrive
          together.
        </p>
      </div>
      <div className="lg:container">
        <div className="space-y-6 relative">
          {/* Left and right blur gradients */}
          <div className="absolute left-0 top-0 bottom-0 w-32 bg-gradient-to-r from-white dark:from-background to-transparent z-10 pointer-events-none" />
          <div className="absolute right-0 top-0 bottom-0 w-32 bg-gradient-to-l from-white dark:from-background to-transparent z-10 pointer-events-none" />
          <Carousel
            opts={{
              loop: true,
            }}
            plugins={[plugin1.current]}
            onMouseLeave={() => plugin1.current.play()}
          >
            <CarouselContent>
              {testimonials1.map((testimonial, index) => (
                <CarouselItem key={index} className="basis-auto">
                  <Card className="max-w-96 p-6 select-none bg-white/80 dark:bg-black/60 backdrop-blur-md border border-neutral-200 dark:border-neutral-800 shadow-md rounded-2xl">
                    <div className="mb-4 flex gap-4 items-center">
                      <Avatar className="size-10 rounded-full ring-2 ring-[#4a90e2]/60 shadow">
                        <AvatarImage
                          src={testimonial.avatar}
                          alt={testimonial.name}
                        />
                      </Avatar>
                      <div className="text-sm">
                        <p className="font-semibold text-neutral-900 dark:text-white">
                          {testimonial.name}
                        </p>
                        <p className="text-muted-foreground">
                          {testimonial.role}
                        </p>
                      </div>
                    </div>
                    <q className="text-base text-neutral-700 dark:text-neutral-200 italic">
                      {testimonial.content}
                    </q>
                  </Card>
                </CarouselItem>
              ))}
            </CarouselContent>
          </Carousel>
          <Carousel
            opts={{
              loop: true,
            }}
            plugins={[plugin2.current]}
            onMouseLeave={() => plugin2.current.play()}
          >
            <CarouselContent>
              {testimonials2.map((testimonial, index) => (
                <CarouselItem key={index} className="basis-auto">
                  <Card className="max-w-96 p-6 select-none bg-white/80 dark:bg-black/60 backdrop-blur-md border border-neutral-200 dark:border-neutral-800 shadow-md rounded-2xl">
                    <div className="mb-4 flex gap-4 items-center">
                      <Avatar className="size-10 rounded-full ring-2 ring-[#2ED2C9]/60 shadow">
                        <AvatarImage
                          src={testimonial.avatar}
                          alt={testimonial.name}
                        />
                      </Avatar>
                      <div className="text-sm">
                        <p className="font-semibold text-neutral-900 dark:text-white">
                          {testimonial.name}
                        </p>
                        <p className="text-muted-foreground">
                          {testimonial.role}
                        </p>
                      </div>
                    </div>
                    <q className="text-base text-neutral-700 dark:text-neutral-200 italic">
                      {testimonial.content}
                    </q>
                  </Card>
                </CarouselItem>
              ))}
            </CarouselContent>
          </Carousel>
        </div>
      </div>
    </section>
  );
};

export { TestimonialSection };
