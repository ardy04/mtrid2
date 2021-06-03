package com.mtrid2.temanikm

import androidx.appcompat.app.AppCompatActivity
import android.os.Bundle
import android.view.Menu
import android.view.MenuItem
import android.view.View
import android.widget.AdapterView
import android.widget.ArrayAdapter
import android.widget.Spinner

class AddUpdateItemActivity : AppCompatActivity(), View.OnClickListener, AdapterView.OnItemSelectedListener {
    private var spinner: Spinner? = null
    private var arrayAdapter: ArrayAdapter<String>? = null

    private var itemList = arrayOf(
            "Lemari",
            "Pintu",
            "Meja",
            "Kursi"
    )

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_add_update_item)

        spinner = findViewById(R.id.spinners)
        arrayAdapter = ArrayAdapter(applicationContext, android.R.layout.simple_spinner_item, itemList)
        spinner?.adapter = arrayAdapter
        spinner?.setSelection(0)
        spinner?.onItemSelectedListener = this
    }

    override fun onCreateOptionsMenu(menu: Menu): Boolean {
        menuInflater.inflate(R.menu.menu_form, menu)
        return super.onCreateOptionsMenu(menu)
    }

    override fun onOptionsItemSelected(item: MenuItem): Boolean {
        when (item.itemId) {
            //DELETE ITEM
            //R.id.action_delete -> showAlertDialog(ALERT_DIALOG_DELETE)
            //android.R.id.home -> showAlertDialog(ALERT_DIALOG_CLOSE)
        }
        return super.onOptionsItemSelected(item)
    }

    override fun onClick(v: View?) {
        TODO("Not yet implemented")
    }

    override fun onItemSelected(parent: AdapterView<*>?, view: View?, position: Int, id: Long) {
        var items: String = parent?.getItemAtPosition(position) as String
    }

    override fun onNothingSelected(parent: AdapterView<*>?) {
        TODO("Not yet implemented")
    }
}