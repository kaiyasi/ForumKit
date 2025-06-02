import { Link } from 'react-router-dom'

const Navbar = () => {
  return (
    <nav className="bg-white shadow">
      <div className="container mx-auto px-4">
        <div className="flex justify-between h-16">
          <div className="flex">
            <Link to="/" className="flex items-center">
              <span className="text-xl font-bold text-primary-600">匿名校園</span>
            </Link>
          </div>
          
          <div className="flex items-center space-x-4">
            <Link to="/login" className="text-gray-600 hover:text-primary-600">
              登入
            </Link>
            <Link to="/register" className="bg-primary-600 text-white px-4 py-2 rounded-md hover:bg-primary-700">
              註冊
            </Link>
          </div>
        </div>
      </div>
    </nav>
  )
}

export default Navbar 