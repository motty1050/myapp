export default function MLAppCard({ app, onClick }) {
    return (
      <div 
        onClick={onClick}
        className="border rounded-lg p-4 hover:shadow cursor-pointer"
      >
        <h3 className="text-xl">{app.name}</h3>
        <p className="text-sm text-gray-600">{app.description}</p>
      </div>
    )
  }
  