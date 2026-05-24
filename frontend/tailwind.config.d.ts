declare const _default: {
    content: string[];
    theme: {
        extend: {
            colors: {
                hud: {
                    base: string;
                    glow: string;
                    blue: string;
                    soft: string;
                };
            };
            fontFamily: {
                display: [string, string];
                body: [string, string];
            };
            boxShadow: {
                hud: string;
                panel: string;
            };
            backgroundImage: {
                "hud-grid": string;
            };
            animation: {
                scan: string;
                float: string;
                pulseGlow: string;
            };
            keyframes: {
                scan: {
                    "0%": {
                        transform: string;
                    };
                    "100%": {
                        transform: string;
                    };
                };
                float: {
                    "0%, 100%": {
                        transform: string;
                    };
                    "50%": {
                        transform: string;
                    };
                };
                pulseGlow: {
                    "0%, 100%": {
                        opacity: string;
                        boxShadow: string;
                    };
                    "50%": {
                        opacity: string;
                        boxShadow: string;
                    };
                };
            };
        };
    };
    plugins: any[];
};
export default _default;
