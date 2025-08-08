import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { useAuth } from '../contexts/AuthContext';
import { Button } from '../components/ui/button';
import { Link } from 'react-router-dom';

interface Post {
  id: number;
  title: string;
  content: string;
  created_at: string;
  author: {
    username: string;
  };
}

const Home = () => {
  const [posts, setPosts] = useState<Post[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const { isAuthenticated } = useAuth();

  useEffect(() => {
    fetch('http://localhost:8000/api/v1/posts')
      .then(response => {
        if (!response.ok) {
          throw new Error('Network response was not ok');
        }
        return response.json();
      })
      .then(data => {
        setPosts(data);
        setLoading(false);
      })
      .catch(err => {
        setError('無法載入貼文，請稍後再試。');
        setLoading(false);
      });
  }, []);

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('zh-TW', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  };

  if (loading) {
    return (
      <div className="container mx-auto px-4 py-12">
        <div className="max-w-3xl mx-auto">
          <div className="h-10 w-64 animate-pulse rounded-lg bg-muted/80 mb-4 mx-auto" />
          <div className="h-6 w-80 animate-pulse rounded-lg bg-muted/80 mb-12 mx-auto" />
          <div className="space-y-8">
            {[...Array(3)].map((_, i) => (
              <Card key={i} className="border-border/40">
                <CardHeader>
                  <div className="h-7 w-3/4 animate-pulse rounded-lg bg-muted/80 mb-3" />
                  <div className="h-4 w-1/4 animate-pulse rounded-lg bg-muted/80" />
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    <div className="h-4 w-full animate-pulse rounded-lg bg-muted/80" />
                    <div className="h-4 w-5/6 animate-pulse rounded-lg bg-muted/80" />
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="container mx-auto px-4 py-12">
        <div className="max-w-3xl mx-auto text-center">
          <p className="text-destructive text-lg">{error}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-12">
      <div className="max-w-3xl mx-auto">
        <header className="mb-16 text-center">
          <h1 className="text-4xl font-bold tracking-tight lg:text-5xl mb-4 text-primary">
            探索、分享、交流
          </h1>
          <p className="text-lg text-muted-foreground leading-relaxed">
            一個屬於你的角落，在這裡自由發聲，尋找共鳴。
          </p>
        </header>

        {!isAuthenticated && (
          <Card className="mb-12 text-center bg-card/80 backdrop-blur-sm">
            <CardHeader>
              <CardTitle className="text-2xl">加入我們的討論</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <p className="text-muted-foreground">登入或註冊帳號，開始你的第一篇分享！</p>
              <div className="flex justify-center gap-4">
                <Button asChild>
                  <Link to="/login">登入</Link>
                </Button>
                <Button variant="secondary" asChild>
                  <Link to="/signup">註冊</Link>
                </Button>
              </div>
            </CardContent>
          </Card>
        )}

        <div className="space-y-8">
          {posts.length > 0 ? (
            posts.map((post) => (
              <Card key={post.id} className="hover:border-primary/50 transition-colors duration-300 bg-card/80 backdrop-blur-sm">
                <CardHeader className="pb-4">
                  <CardTitle className="text-2xl font-semibold leading-tight tracking-wide">
                    {post.title}
                  </CardTitle>
                  <div className="flex items-center text-sm text-muted-foreground pt-2">
                    <span>{post.author.username}</span>
                    <span className="mx-2">•</span>
                    <span>{formatDate(post.created_at)}</span>
                  </div>
                </CardHeader>
                <CardContent>
                  <p className="text-foreground/80 leading-relaxed line-clamp-3">
                    {post.content}
                  </p>
                </CardContent>
              </Card>
            ))
          ) : (
            <div className="text-center py-16">
              <p className="text-muted-foreground text-lg">宇宙的中心一片寂靜... 等待第一顆星辰的誕生。</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default Home;