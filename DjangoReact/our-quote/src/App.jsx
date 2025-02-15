import { useState, useEffect } from "react";
import axios from "axios";

function App() {
  const [details, setDetails] = useState(null);

  useEffect(() => {
    axios
      .get("http://127.0.0.1:8000/wel/")
      .then((response) => {
        console.log(response.data);
        setDetails(response.data);
      })
      .catch((error) => {
        console.log(error);
      });
  }, []);

  const handleSubmit = (e) => {
    console.log(e);
  };

  return (
    <div className="container jumbotron">
      <form onSubmit={handleSubmit}>
        <div className="input-group mb-3">
          <div className="input-group-prepend">
            <span className="input-group-text" id="basic-addon1">
              {" "}
              Author
              {" "}
            </span>
          </div>
          <input type="text" className="form-control" placeholder="name of Author" aria-label="Username" aria-describedby="basic-addon1" 
          value={details && details[0].name}/>
        </div>
      </form>
    </div>
  );
}

export default App;
