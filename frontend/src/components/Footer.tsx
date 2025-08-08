const Footer = () => {
  return (
    <footer className="py-8 mt-16">
      <div className="container mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-center items-center">
          <p className="text-sm text-muted-foreground">
            © {new Date().getFullYear()} ForumKit. All Rights Reserved.
          </p>
        </div>
      </div>
    </footer>
  );
};

export default Footer;
