import { Link } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { Button } from './ui/button';

const Navbar = () => {
  const { user, logout } = useAuth();

  return (
    <nav className="flex items-center space-x-6">
      {user ? (
        <div className="flex items-center space-x-4">
          <span className="text-sm text-muted-foreground">
            {user.username}
          </span>
          <Button 
            variant="ghost" 
            size="sm" 
            onClick={logout}
            className="text-sm font-medium"
          >
            登出
          </Button>
        </div>
      ) : (
        <div className="flex items-center space-x-4">
          <Link to="/login">
            <Button variant="ghost" size="sm" className="text-sm font-medium">
              登入
            </Button>
          </Link>
          <Link to="/signup">
            <Button size="sm" className="text-sm font-medium">
              註冊
            </Button>
          </Link>
        </div>
      )}
    </nav>
  );
};

export default Navbar;
