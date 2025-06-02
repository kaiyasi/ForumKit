const Home = () => {
  return (
    <div className="space-y-8">
      <section className="text-center">
        <h1 className="text-4xl font-bold text-gray-900 mb-4">
          歡迎來到匿名校園討論平台
        </h1>
        <p className="text-xl text-gray-600">
          在這裡，你可以自由地分享想法，討論校園生活
        </p>
      </section>

      <section className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {/* 這裡將來會顯示熱門討論主題 */}
        <div className="bg-white p-6 rounded-lg shadow">
          <h2 className="text-xl font-semibold mb-4">熱門討論</h2>
          <p className="text-gray-600">敬請期待...</p>
        </div>

        <div className="bg-white p-6 rounded-lg shadow">
          <h2 className="text-xl font-semibold mb-4">最新動態</h2>
          <p className="text-gray-600">敬請期待...</p>
        </div>

        <div className="bg-white p-6 rounded-lg shadow">
          <h2 className="text-xl font-semibold mb-4">校園公告</h2>
          <p className="text-gray-600">敬請期待...</p>
        </div>
      </section>
    </div>
  )
}

export default Home 