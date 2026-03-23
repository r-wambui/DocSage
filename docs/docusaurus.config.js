// @ts-check
/** @type {import('@docusaurus/types').Config} */
const config = {
  title: "DocSage",
  tagline: "Chat with your local documents privately.",
  favicon: "img/favicon.ico",

  url: "https://r-wambui.github.io",
  baseUrl: "/",

  organizationName: "r-wambui",
  projectName: "DocSage",

  onBrokenLinks: "throw",
  onBrokenMarkdownLinks: "warn",

  i18n: {
    defaultLocale: "en",
    locales: ["en"],
  },

  presets: [
    [
      "classic",
      /** @type {import('@docusaurus/preset-classic').Options} */
      ({
        docs: {
          sidebarPath: "./sidebars.js",
          routeBasePath: "/",
        },
        blog: false,

      }),
    ],
  ],

  themeConfig:
    /** @type {import('@docusaurus/preset-classic').ThemeConfig} */
    ({
      navbar: {
        title: " DocSage",
        items: [
          {
            type: "docSidebar",
            sidebarId: "tutorialSidebar",
            position: "left",
            label: "Docs",
          },
          {
            href: "https://github.com/r-wambui/DocSage",
            label: "GitHub",
            position: "right",
          },
        ],
      },
      footer: {
        style: "dark",
        links: [
          
          {
            title: "Built With",
            items: [
              {
                label: "llama.cpp",
                href: "https://github.com/ggerganov/llama.cpp",
              },
              {
                label: "nomic-embed-text-v1",
                href: "https://huggingface.co/nomic-ai/nomic-embed-text-v1",
              },
              {
                label: "ChromaDB",
                href: "https://www.trychroma.com",
              },
              {
                label: "Streamlit",
                href: "https://streamlit.io",
              },
            ],
          },
          {
            title: "Project",
            items: [
              {
                label: "GitHub",
                href: "https://github.com/r-wambui/DocSage",
              },
              {
                label: "Report an Issue",
                href: "https://github.com/r-wambui/DocSage/issues",
              },
            ],
          },
        ],
        copyright: `DocSage — 100% local, 100% private. Built with llama.cpp + ChromaDB.`,
      },
      prism: {
        theme: require("prism-react-renderer").themes.github,
        darkTheme: require("prism-react-renderer").themes.dracula,
        additionalLanguages: ["bash", "python"],
      },
      colorMode: {
        defaultMode: "light",
        respectPrefersColorScheme: true,
      },
    }),
};

module.exports = config;