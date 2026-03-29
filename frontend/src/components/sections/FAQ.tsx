import { FAQTabs } from "../ui/faq-tabs";

export const FAQ = () => {
  const categories = {
    "general": "General",
    "workflows": "Audit Workflows",
    "security": "Security & Compl",
    "pricing": "Pricing & Plans"
  };

  const faqData = {
    "general": [
      {
        question: "What is AuditPilot?",
        answer: "AuditPilot is a comprehensive audit workflow management platform designed by top enterprise software engineers. It helps teams track, review, and generate audit insights automatically using AI."
      },
      {
        question: "How long does it take to deploy AuditPilot?",
        answer: "For most teams, deploying AuditPilot takes less than 24 hours. Our automated onboarding agent walks you through integrating your existing systems so you can run your first audit immediately."
      },
      {
        question: "Can I try before committing to a paid plan?",
        answer: "Yes, we offer a Free Starter tier that allows you to run up to 5 automated workflows per day, making it perfect for prototyping and small-team evaluations."
      }
    ],
    "workflows": [
      {
        question: "How do automated briefings work?",
        answer: "AuditPilot's AI agents analyze your current system state against compliance rulesides and automatically generate structured email briefings. These are sent directly to your stakeholders prior to crucial alignment meetings."
      },
      {
        question: "Which integrations are supported?",
        answer: "We currently support direct integrations with AWS CloudTrail, GitHub Advanced Security, and standard REST API endpoints. We are constantly expanding our native webhook support."
      },
      {
        question: "Can I customize the workflow triggers?",
        answer: "Absolutely. Pro and Enterprise users can define custom CRON jobs or webhook triggers that initiate audit workflows based on highly specific infrastructure events."
      }
    ],
    "security": [
      {
        question: "Is my data secure?",
        answer: "Yes. AuditPilot was built with enterprise-grade security from day one. All data is encrypted at rest (AES-256) and in transit (TLS 1.3), passing stringent SOC2 Type II compliance checks."
      },
      {
        question: "Do you train AI models on my data?",
        answer: "No. Your proprietary infrastructure logs and audit results are strictly siloed. We guarantee zero cross-contamination and never use client data to train public or foundational LLMs."
      },
      {
        question: "What access control systems do you support?",
        answer: "We support SAML, Single Sign-On (SSO) via Okta, Google Workspace, and Microsoft Entra ID. You can also implement fine-grained Role-Based Access Control (RBAC) across your workspaces."
      }
    ],
    "pricing": [
      {
        question: "How is billing calculated?",
        answer: "Our billing is a hybrid model. You pay a simple, flat monthly/yearly fee for your tier, which includes standard workflow executions. Heavy LLM analysis is billed transparently purely on a per-call usage scale."
      },
      {
        question: "What happens if I exceed my Free tier limits?",
        answer: "Your automated workflows will safely queue and pause until the limits soft-reset the next day. If you need immediate execution, you can quickly upgrade to Pro without dropping queued actions."
      },
      {
        question: "Do you offer SLA guarantees?",
        answer: "Yes. Enterprise clients receive a 99.99% uptime SLA guarantee along with dedicated Technical Account Managers and priority 24/7 incident response channels."
      }
    ]
  };

  return (
    <FAQTabs 
      title="Common Queries"
      subtitle="Help Center"
      categories={categories}
      faqData={faqData}
      className="max-w-4xl mx-auto"
    />
  );
};
