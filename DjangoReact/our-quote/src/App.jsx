import { useState, useEffect } from "react";
import axios from "axios";

const fetch = (state, setState) => {
  axios
      .get("http://127.0.0.1:8000/wel/")
      .then((response) => {
        console.log(response.data);
        const details = response.data;
        setState((prevState) => ({
          ...prevState,
          details: details,
          refresh: false
        }));
        console.log(state);
      })
      .catch((error) => {
        console.log(error);
      });
}

function App() {
  const [state, setState] = useState({
    details: [],
    user: '',
    quote: '',
    refresh: false,
  })

  useEffect(() => {
    fetch(state, setState);
  },[]);

  const renderSwitch = (param) => {
    switch (param + 1) {
      case 1:
        return "primary ";
      case 2:
        return "secondary ";
      case 3:
        return "success ";
      case 4:
        return "danger ";
      case 5:
        return "warning ";
      case 6:
        return "info ";
      default:
        return "yellow ";
    }
  }

  const handleSubmit = (e) => {
    e.preventDefault();
    axios
    .post('http://127.0.0.1:8000/wel/', {
      name: state.user,
      detail: state.quote,
    })
    .then((res) =>{
      console.log(res)
      setState({user:'',quote:''});
      fetch(state, setState)

    })
    .catch((err) => {console.log(err)})
  };

  const handleInput = (e) => {
    const {name, value} = e.target;
    setState({
      ...state,
      [name]:value
    })
  } 

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
          value={state.user}
          name="user"
          onChange={handleInput}/>
        </div>

        <div className="input-group mv-3">
          <div className="input-group-prepend">
            <span className="input-group-text">
              your qoute
            </span>
          </div>

          <textarea className="form-control"
          aria-label="with textarea"
          placeholder="Tell us what you think of ....."
          value={state.quote}
          name="quote"
          onChange={handleInput}
          >
          </textarea>
        </div>
        <button className="btn btn-primary mb-5" type="submit">
          Submit
        </button>
      </form>
      <hr
        style={{
          color:"#000",
          backgroundColor:"#000",
          height: 0.5,
          borderColor:"#000",
        }}
      />

      {state.details && state.details.map((item, index) => (
        <div key={index}>
          <div className="card shadow-lg">
            <div className={"bg-"+renderSwitch(index%6) + " card-body"}>
              quote {index+1}
            </div>
            <div className="card-body">
              <blockquote className={"text-"+renderSwitch(index % 6) + " blockqoute-footer mb-0"}>
                <h1> {item.detail} </h1>
                <footer className="blockquote-footer">
{" "}
<cite title="Source Title">{item.name}</cite>
                </footer>
              </blockquote>
            </div>
          </div>
          <span className="border border-primary"></span>
        </div>
      ))}
    </div>
  );
}

export default App;
