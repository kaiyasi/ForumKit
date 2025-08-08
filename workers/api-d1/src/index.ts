import { Router, IRequest } from 'itty-router';

// Define the environment interface to include the D1 database binding
export interface Env {
	D1_DATABASE: D1Database;
}

// Define a request type that includes the environment
export type RequestWithEnv = IRequest & { env: Env };

const router = Router();

// Middleware to handle JSON responses and errors
const withJson = (handler: (request: RequestWithEnv) => any) => async (request: RequestWithEnv) => {
    try {
        const result = await handler(request);
        return new Response(JSON.stringify(result), {
            headers: { 'Content-Type': 'application/json' },
        });
    } catch (e: any) {
        return new Response(JSON.stringify({ error: e.message }), {
            status: 500,
            headers: { 'Content-Type': 'application/json' },
        });
    }
};

// GET /api/posts - Fetch all posts
router.get('/api/posts', withJson(async (request: RequestWithEnv) => {
    const { results } = await request.env.D1_DATABASE.prepare(
        'SELECT id, title, content, author_id, created_at FROM posts ORDER BY created_at DESC'
    ).all();

    // Here you might want to fetch author details for each post, 
    // but for simplicity, we'll return author_id for now.
    return results;
}));

// 404 handler
router.all('*', () => new Response('Not Found.', { status: 404 }));

export default {
	async fetch(
		request: Request,
		env: Env,
		ctx: ExecutionContext
	): Promise<Response> {
		return router.handle(request, env, ctx);
	},
};
