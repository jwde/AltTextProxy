@jwde and @jbronen
COMP 112 - Fall 2015

#Building an Efficient HTTP Proxy for Accessibility

For our final project, we chose to design and implement an HTTP proxy primarily designed for use by people with disabilities. We wrote our proxy in python and implemented the following features:
<ol>
<li>Reverse image alt-text generation: we inject javascript on pages containing images without alt-text to asynchronously perform a reverse image search to Google. We then parse the results to return the best possible description.</li>
<li>Link magnification: We implemented a magnification system to increase the size of links by altering the styling of HTML pages for increased ease of use.</li>
</li>Performance
  <ol><li>Image Caching: We developed a system to store image paths and their respective alt-texts in a cache for performance benefits.</li>
  <li>JavaScript Injection: We developed a system to asynchronously process alt-text requests so the majority of the page could load without waiting for the process to complete.</li>
  </ol></li></ol>

###REVERSE IMAGE ALT-TEXT GENERATION:
<p>Before serving HTML content, we scan the document for images without alt-text using regular expressions. If we find any, we assign a special class to the image, and inject javascript into the page to asynchronously request the alt-text using AJAX, and then add it to the alt field in the image itself. If the image does not exist in our cache, we use cURL to process a reverse-image search to Google. We then use Beautiful Soup to parse the results and return the first description, which is added to an alt field within the image by the injector.</p>
<p>Many visually impaired users use screen readers, such as WebbIE on Windows or the Fang extension for Firefox, to view text-only versions HTML documents. While many popular, large-scale websites include the alt tag, which replaces image on many of these screen readers, many websites with user-generated content, such as tumblr or WordPress, contain images without any alt-text. This tool aims to make those websites, as well as any others that contain images without alt-text more accessible.</p>

###LINK MAGNIFICATION:


###PERFORMANCE:
<ol><li>######Image Caching:

</li>
<li>######Javascript Injector:

</li></ol>
###CONCLUSION:
