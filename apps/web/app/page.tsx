import { Hero } from "@/components/landing/Hero";
import { UploadDropzone } from "@/components/landing/UploadDropzone";
import { FeatureGrid } from "@/components/landing/FeatureGrid";
import { HowItWorks } from "@/components/landing/HowItWorks";
import { RecentAnalyses } from "@/components/landing/RecentAnalyses";

export default function HomePage() {
  return (
    <>
      <Hero />
      <UploadDropzone />
      <FeatureGrid />
      <HowItWorks />
      <RecentAnalyses />
    </>
  );
}
