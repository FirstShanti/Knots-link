const setInStorage = (key, value, type='LOCAL') => {
    try {
      const serializedValue = JSON.stringify(value);
      let storage = sessionStorage
      if (type == 'LOCAL') {
        storage = localStorage
      }
      storage.setItem(key, serializedValue);
    } catch (err) {
      // TODO: log error?
    }
  };
  
const getFromStorage = (key, type='LOCAL') => {
  try {
    let storage = sessionStorage
    if (type == 'LOCAL') {
      storage = localStorage
    }
    const value = storage.getItem(key);
    if (value === null) {
      return undefined;
    }
    return JSON.parse(value);
  } catch (err) {
    return undefined;
  }
};

const removeFromStorage = (key, type='LOCAL') => {
  try {
    let storage = sessionStorage
    if (type == 'LOCAL') {
      storage = localStorage
    }
    storage.removeItem(key);
  } catch (err) {
    console.error(err)
  }
}

function getCookie(name) {
  const value = `; ${document.cookie}`;
  const parts = value.split(`; ${name}=`);
  if (parts.length === 2) return parts.pop().split(';').shift();
}