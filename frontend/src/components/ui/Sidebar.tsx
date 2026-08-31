import React, { useState, createContext, useContext } from "react";
import { AnimatePresence, motion } from "motion/react";
import { Menu, X } from "lucide-react";
import { cn } from "../../lib/utils";

interface Links {
  label: string;
  href?: string;
  icon: React.ReactNode;
  id?: string;
  badge?: string;
  onClick?: () => void;
  active?: boolean;
}

interface SidebarContextProps {
  open: boolean;
  setOpen: React.Dispatch<React.SetStateAction<boolean>>;
  animate: boolean;
}

const SidebarContext = createContext<SidebarContextProps | undefined>(
  undefined
);

export const useSidebar = () => {
  const context = useContext(SidebarContext);
  if (!context) {
    throw new Error("useSidebar must be used within a SidebarProvider");
  }
  return context;
};

export const SidebarProvider = ({
  children,
  open: openProp,
  setOpen: setOpenProp,
  animate = true,
}: {
  children: React.ReactNode;
  open?: boolean;
  setOpen?: React.Dispatch<React.SetStateAction<boolean>>;
  animate?: boolean;
}) => {
  const [openState, setOpenState] = useState(false);

  const open = openProp !== undefined ? openProp : openState;
  const setOpen = setOpenProp !== undefined ? setOpenProp : setOpenState;

  return (
    <SidebarContext.Provider value={{ open, setOpen, animate }}>
      {children}
    </SidebarContext.Provider>
  );
};

export const Sidebar = ({
  children,
  open,
  setOpen,
  animate,
}: {
  children: React.ReactNode;
  open?: boolean;
  setOpen?: React.Dispatch<React.SetStateAction<boolean>>;
  animate?: boolean;
}) => {
  return (
    <SidebarProvider open={open} setOpen={setOpen} animate={animate}>
      {children}
    </SidebarProvider>
  );
};

export const SidebarBody = (props: React.ComponentProps<typeof motion.div>) => {
  return (
    <>
      <DesktopSidebar {...props} />
      <MobileSidebar {...(props as React.ComponentProps<"div">)} />
    </>
  );
};

export const DesktopSidebar = ({
  className,
  children,
  ...props
}: React.ComponentProps<typeof motion.div>) => {
  const { open, setOpen, animate } = useSidebar();
  return (
    <motion.div
      className={cn(
        "h-full px-3.5 py-4 hidden md:flex md:flex-col bg-theme-sidebar text-theme-primary border-r border-theme-subtle backdrop-blur-md shrink-0 z-30 transition-all duration-300",
        className
      )}
      animate={{
        width: animate ? (open ? "260px" : "72px") : "260px",
      }}
      onMouseEnter={() => setOpen(true)}
      onMouseLeave={() => setOpen(false)}
      {...props}
    >
      {children}
    </motion.div>
  );
};

export const MobileSidebar = ({
  className,
  children,
  ...props
}: React.ComponentProps<"div">) => {
  const { open, setOpen } = useSidebar();
  return (
    <div
      className={cn(
        "h-14 px-4 flex flex-row md:hidden items-center justify-between bg-theme-sidebar border-b border-theme-subtle w-full z-30",
        className
      )}
      {...props}
    >
      <div className="flex justify-between items-center w-full z-20">
        <button
          id="mobile-menu-button"
          aria-label="Toggle menu"
          onClick={() => setOpen(!open)}
          className="p-1.5 rounded-lg text-theme-muted hover:text-theme-primary hover:bg-theme-card-hover transition-colors"
        >
          <Menu className="w-5 h-5" />
        </button>
      </div>
      <AnimatePresence>
        {open && (
          <motion.div
            initial={{ x: "-100%", opacity: 0 }}
            animate={{ x: 0, opacity: 1 }}
            exit={{ x: "-100%", opacity: 0 }}
            transition={{
              duration: 0.25,
              ease: "easeInOut",
            }}
            className={cn(
              "fixed h-full w-4/5 max-w-xs inset-0 bg-theme-page p-6 z-[100] flex flex-col justify-between border-r border-theme-subtle",
              className
            )}
          >
            <div
              className="absolute right-4 top-4 z-50 text-theme-muted hover:text-theme-primary cursor-pointer p-1"
              onClick={() => setOpen(!open)}
            >
              <X className="w-5 h-5" />
            </div>
            {children}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

export const SidebarLink = ({
  link,
  className,
  ...props
}: {
  link: Links;
  className?: string;
  [key: string]: any;
}) => {
  const { open, animate } = useSidebar();
  return (
    <button
      id={`nav-link-${link.id || link.label.toLowerCase().replace(/\s+/g, "-")}`}
      onClick={link.onClick}
      className={cn(
        "flex items-center justify-start gap-3 group/sidebar py-2 px-2.5 rounded-xl w-full text-left transition-all duration-150 relative font-sans",
        link.active
          ? "bg-theme-cyan-subtle text-[#00D1FF] font-medium border border-theme-cyan"
          : "text-theme-muted hover:text-theme-primary hover:bg-theme-card-hover",
        className
      )}
      {...props}
    >
      <div className="shrink-0 text-theme-muted group-hover/sidebar:text-[#00D1FF] transition-colors">
        {link.icon}
      </div>

      <motion.span
        animate={{
          display: animate ? (open ? "inline-block" : "none") : "inline-block",
          opacity: animate ? (open ? 1 : 0) : 1,
        }}
        className="text-xs tracking-wide whitespace-nowrap overflow-hidden text-ellipsis flex-1 font-medium"
      >
        {link.label}
      </motion.span>

      {link.badge && open && (
        <motion.span
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="text-[9px] uppercase font-mono px-1.5 py-0.5 rounded-md bg-theme-card-sub text-[#00D1FF] border border-theme-subtle"
        >
          {link.badge}
        </motion.span>
      )}
    </button>
  );
};
