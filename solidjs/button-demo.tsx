import { render, For } from "solid-js/web";
import { createSignal, children } from "solid-js";
import { createStore } from "solid-js/store";

function Button(props) {
  const getChildren = children(() => props.children);
  const getOnClick = () => props.onClick;
  return (
    <button type="button" onClick={getOnClick()}>
      {getChildren()}
    </button>
  );
}

function App() {
  const [store, setStore] = createStore({ count: 0 });
  const increment = () => {
    setStore('count', store.count + 1);
    console.log(`store.count=${store.count}`);
  };
  return (
    <Button onClick={increment}>
      {store.count}
    </Button>
  );
}

render(() => <App />, document.getElementById("app")!);
